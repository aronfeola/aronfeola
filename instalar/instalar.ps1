# =====================================================================
#  Instalador del Socio de negocios 3D  (Windows 10 / 11)
#
#  Instala lo que hace falta, baja tu carpeta de trabajo y crea los accesos
#  directos en el Escritorio. Se puede ejecutar mas de una vez sin problema:
#  lo que ya esta instalado se saltea.
# =====================================================================

$Repo    = 'https://github.com/aronfeola/aronfeola.git'
$Rama    = 'claude/meta-ads-creative-agent-9zdnfr'
$Carpeta = Join-Path $env:USERPROFILE 'Documents\Socio3D'
$Log     = Join-Path $env:USERPROFILE 'Documents\instalacion-socio3d.txt'

$ErrorActionPreference = 'Continue'
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch { }
try { Start-Transcript -Path $Log -Force | Out-Null } catch { }

function Titulo($t) { Write-Host ''; Write-Host $t -ForegroundColor Cyan }
function Bien($t)   { Write-Host "   [OK] $t" -ForegroundColor Green }
function Aviso($t)  { Write-Host "   [!]  $t" -ForegroundColor Yellow }
function Info($t)   { Write-Host "        $t" }

function Terminar($t) {
    Write-Host ''
    Write-Host "   [X]  $t" -ForegroundColor Red
    Write-Host ''
    Write-Host '   La instalacion se detuvo. Mandale una captura de esta ventana' -ForegroundColor Red
    Write-Host "   (o el archivo $Log) a Claude y lo resolvemos." -ForegroundColor Red
    try { Stop-Transcript | Out-Null } catch { }
    exit 1
}

# Despues de instalar algo, Windows no actualiza el PATH de esta ventana: se vuelve a leer.
function Actualizar-Path {
    $maquina = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $usuario = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$maquina;$usuario"
}

function Existe($nombre) {
    return [bool](Get-Command $nombre -ErrorAction SilentlyContinue)
}

function Instalar-Con-Winget($id, $nombre) {
    Aviso "Instalando $nombre (puede pedirte permiso de administrador: aceptalo)..."
    $global:LASTEXITCODE = 0
    winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements
    Actualizar-Path
}

# En Windows, "python" a veces es un atajo a la Microsoft Store que no es Python de verdad.
function Buscar-Python {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd -and ($cmd.Source -notlike '*WindowsApps*')) { return $cmd.Source }
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $global:LASTEXITCODE = 0
        $exe = & py -3 -c "import sys; print(sys.executable)"
        if (($LASTEXITCODE -eq 0) -and $exe) { return ($exe | Select-Object -First 1).Trim() }
    }
    return $null
}

function Atajo($nombre, $destino, $argumentos, $trabajo) {
    $escritorio = [Environment]::GetFolderPath('Desktop')
    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut((Join-Path $escritorio "$nombre.lnk"))
    $lnk.TargetPath = $destino
    if ($argumentos) { $lnk.Arguments = $argumentos }
    if ($trabajo) { $lnk.WorkingDirectory = $trabajo }
    $lnk.Save()
}

Titulo '=== Socio de negocios 3D: instalacion ==='
Info "Tu carpeta de trabajo va a quedar en: $Carpeta"
Info 'Tarda unos minutos. Puede pedirte permisos y abrir una ventana para iniciar sesion en GitHub: aceptalo.'

# ---------------------------------------------------------------- 1
Titulo '1/7  Revisando tu Windows'
if (-not (Existe 'winget')) {
    Terminar 'No encuentro "winget". Abri la Microsoft Store, busca "Instalador de aplicacion" (App Installer), actualizalo y volve a ejecutar este instalador.'
}
Bien 'winget disponible'

# ---------------------------------------------------------------- 2
Titulo '2/7  Git (para guardar y sincronizar tu negocio)'
if (-not (Existe 'git')) { Instalar-Con-Winget 'Git.Git' 'Git' }
if (-not (Existe 'git')) {
    Terminar 'No pude instalar Git. Descargalo de https://git-scm.com/download/win, instalalo y volve a ejecutar este instalador.'
}
Bien ((git --version) -join ' ')

# ---------------------------------------------------------------- 3
Titulo '3/7  Python'
$Python = Buscar-Python
if (-not $Python) {
    Instalar-Con-Winget 'Python.Python.3.12' 'Python 3.12'
    $Python = Buscar-Python
}
if (-not $Python) {
    Terminar 'No pude instalar Python. Descargalo de https://www.python.org/downloads/ (marca "Add python.exe to PATH") y volve a ejecutar este instalador.'
}
Bien "Python: $Python"

# Que "python" funcione en cualquier ventana nueva (se pone primero, antes del atajo de la Store).
$dirPython = Split-Path $Python
$pathUsuario = [Environment]::GetEnvironmentVariable('Path', 'User')
if (-not $pathUsuario) { $pathUsuario = '' }
foreach ($d in @((Join-Path $dirPython 'Scripts'), $dirPython)) {
    if (($pathUsuario -split ';') -notcontains $d) { $pathUsuario = "$d;$pathUsuario" }
}
[Environment]::SetEnvironmentVariable('Path', $pathUsuario, 'User')
Actualizar-Path

# ---------------------------------------------------------------- 4
Titulo '4/7  Bajando tu carpeta de trabajo'
if (Test-Path (Join-Path $Carpeta '.git')) {
    Info 'Ya estaba descargada: la actualizo.'
    git -C $Carpeta fetch origin $Rama
    git -C $Carpeta checkout $Rama
    git -C $Carpeta pull --rebase --autostash origin $Rama
    if ($LASTEXITCODE -ne 0) {
        Terminar "No pude actualizar la carpeta $Carpeta. Si tenes cambios sin guardar, abri 'Guardar y sincronizar' primero."
    }
} else {
    if (Test-Path $Carpeta) {
        Terminar "La carpeta $Carpeta ya existe pero no es la del negocio. Renombrala o borrala y volve a ejecutar."
    }
    Info 'Si se abre una ventana de GitHub, inicia sesion con tu cuenta.'
    git clone --branch $Rama $Repo $Carpeta
    if ($LASTEXITCODE -ne 0) {
        Terminar 'No pude bajar el repositorio. Revisa que tengas internet y que hayas iniciado sesion en GitHub con la cuenta que tiene el repositorio aronfeola/aronfeola.'
    }
}
if (-not (git -C $Carpeta config user.name))  { git -C $Carpeta config user.name 'Negocio 3D' }
if (-not (git -C $Carpeta config user.email)) { git -C $Carpeta config user.email 'negocio3d@users.noreply.github.com' }
Bien 'Carpeta lista'

# ---------------------------------------------------------------- 5
Titulo '5/7  Librerias de Python (medir anuncios, comparar imagenes)'
$global:LASTEXITCODE = 0
& $Python -m pip install --quiet --upgrade pillow numpy youtube-transcript-api
if ($LASTEXITCODE -ne 0) { Terminar 'No pude instalar las librerias de Python (pillow, numpy).' }
& $Python -c "import PIL, numpy; print('Pillow', PIL.__version__, '- numpy', numpy.__version__)"
Bien 'Librerias instaladas'

# ---------------------------------------------------------------- 6
Titulo '6/7  Node.js y el navegador que genera las imagenes'
if (-not (Existe 'node')) { Instalar-Con-Winget 'OpenJS.NodeJS.LTS' 'Node.js' }
if (-not (Existe 'node')) {
    Terminar 'No pude instalar Node.js. Descargalo de https://nodejs.org (version LTS), instalalo y volve a ejecutar este instalador.'
}
Bien ('Node ' + (node --version))
Push-Location (Join-Path $Carpeta 'agente-marketing')
$global:LASTEXITCODE = 0
npm.cmd install --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { Pop-Location; Terminar 'Fallo "npm install".' }
Info 'Bajando el navegador (Chromium): son unos 150 MB, tarda un poco...'
npx.cmd playwright install chromium
if ($LASTEXITCODE -ne 0) { Pop-Location; Terminar 'No pude bajar el navegador de Playwright.' }
Pop-Location
Bien 'Generador de anuncios listo'

# ---------------------------------------------------------------- 7
Titulo '7/7  Claude Code (el asistente en tu PC)'
$claude = Join-Path $env:USERPROFILE '.local\bin\claude.exe'
if (-not (Test-Path $claude) -and -not (Existe 'claude')) {
    Aviso 'Instalando Claude Code...'
    try { Invoke-RestMethod 'https://claude.ai/install.ps1' | Invoke-Expression }
    catch { Aviso ('No se pudo instalar solo: ' + $_.Exception.Message) }
    Actualizar-Path
}
if ((Test-Path $claude) -or (Existe 'claude')) {
    Bien 'Claude Code instalado'
} else {
    Aviso 'No pude instalar Claude Code automaticamente.'
    Info 'Opcion: instala la app de escritorio de Claude desde https://claude.com/download'
    Info 'y abrila en la carpeta Socio3D (pestana "Code").'
}

# ------------------------------------------------- accesos directos
Titulo 'Creando los accesos directos en el Escritorio'
try {
    Atajo 'Claude - Socio 3D' "$env:SystemRoot\System32\cmd.exe" ('/k cd /d "' + $Carpeta + '" && "%USERPROFILE%\.local\bin\claude.exe"') $Carpeta
    Atajo 'Editor de posteos' (Join-Path $Carpeta 'agente-marketing\herramientas\editor-posteos.html') '' $Carpeta
    Atajo 'Cotizador 3D' (Join-Path $Carpeta 'automatizaciones\cotizador.html') '' $Carpeta
    Atajo 'Guardar y sincronizar' (Join-Path $Carpeta 'sincronizar.bat') '' $Carpeta
    Atajo 'Carpeta Socio 3D' $Carpeta '' $Carpeta
    Bien 'Accesos directos creados'
} catch {
    Aviso ('No pude crear los accesos directos: ' + $_.Exception.Message)
    Info "Igual podes usar todo desde la carpeta $Carpeta"
}

# ------------------------------------------------- prueba final
Titulo 'Prueba final: generando un anuncio de ejemplo'
$prueba = Join-Path $env:TEMP 'prueba-socio3d.png'
if (Test-Path $prueba) { Remove-Item $prueba -Force }
Push-Location (Join-Path $Carpeta 'agente-marketing')
node scripts\render_anuncio.js _ejemplo estilos\_ejemplo\contenido-nuevo.json $prueba
Pop-Location
if (Test-Path $prueba) {
    Bien 'El generador de anuncios funciona. Te abro la imagen de prueba.'
    Start-Process $prueba
} else {
    Aviso 'La prueba del generador de anuncios fallo. Mandale una captura de esta ventana a Claude.'
}

Write-Host ''
Write-Host '==========================  LISTO  ==========================' -ForegroundColor Green
Write-Host ''
Write-Host ' En tu Escritorio tenes:'
Write-Host '   - Claude - Socio 3D       : abre el asistente (la primera vez te pide iniciar sesion)'
Write-Host '   - Editor de posteos       : arma posteos a mano y los descarga en PNG'
Write-Host '   - Cotizador 3D            : calcula precios de impresion'
Write-Host '   - Guardar y sincronizar   : sube tus cambios a GitHub (hacelo al terminar el dia)'
Write-Host '   - Carpeta Socio 3D        : todos tus archivos'
Write-Host ''
Write-Host ' Siguiente paso: abri "Claude - Socio 3D" y escribile: hola'
Write-Host ''
try { Stop-Transcript | Out-Null } catch { }
