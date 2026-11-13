[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$MsixPath,

    [Parameter(Mandatory = $true)]
    [string]$IdentityName
)

$ErrorActionPreference = "Stop"
$packagePath = (Resolve-Path $MsixPath).Path
$releaseDir = Split-Path $packagePath -Parent
$certificatePath = Join-Path $releaseDir "DailyMessage-test.cer"
if (-not (Test-Path $certificatePath)) {
    throw "Certificado de teste não encontrado: $certificatePath"
}

$trustedStore = "Cert:\LocalMachine\TrustedPeople"
$certificate = Import-Certificate -FilePath $certificatePath -CertStoreLocation $trustedStore
$installed = $null
$process = $null

try {
    Write-Host "==> Instalando pacote MSIX para teste"
    Add-AppxPackage -Path $packagePath -ErrorAction Stop

    $installed = Get-AppxPackage -Name $IdentityName | Select-Object -First 1
    if (-not $installed) {
        throw "O pacote $IdentityName não foi registrado após a instalação."
    }

    $settingsExe = Join-Path $installed.InstallLocation "DailyMessage.exe"
    $runnerExe = Join-Path $installed.InstallLocation "DailyMessageRunner.exe"
    if (-not (Test-Path $settingsExe)) { throw "DailyMessage.exe não está presente no pacote instalado." }
    if (-not (Test-Path $runnerExe)) { throw "DailyMessageRunner.exe não está presente no pacote instalado." }

    Write-Host "==> Conferindo manifesto registrado"
    $manifestPath = Join-Path $installed.InstallLocation "AppxManifest.xml"
    [xml]$manifest = Get-Content $manifestPath -Raw
    $namespaces = New-Object System.Xml.XmlNamespaceManager($manifest.NameTable)
    $namespaces.AddNamespace("desktop", "http://schemas.microsoft.com/appx/manifest/desktop/windows10")
    $extension = $manifest.SelectSingleNode("//desktop:Extension[@Category='windows.startupTask']", $namespaces)
    $task = $manifest.SelectSingleNode("//desktop:StartupTask[@TaskId='DailyMessageTask']", $namespaces)
    if (-not $extension -or -not $task) { throw "A extensão DailyMessageTask não foi registrada no manifesto." }
    if ($extension.GetAttribute("Executable") -ne "DailyMessageRunner.exe") {
        throw "A tarefa de inicialização não aponta para DailyMessageRunner.exe."
    }
    if ($task.GetAttribute("Enabled") -ne "false") {
        throw "A tarefa de inicialização deveria vir desativada por padrão."
    }

    Write-Host "==> Executando teste interno com identidade MSIX ativa"
    $process = Start-Process -FilePath $settingsExe -ArgumentList "--msix-self-test" -PassThru -WindowStyle Hidden
    if (-not $process.WaitForExit(30000)) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw "O teste interno do aplicativo excedeu 30 segundos."
    }
    if ($process.ExitCode -ne 0) {
        throw "O teste interno do aplicativo retornou código $($process.ExitCode)."
    }

    Write-Host "MSIX_INSTALL_TEST=PASS"
    Write-Host "MSIX_STARTUP_TASK_MANIFEST=PASS"
    Write-Host "MSIX_PACKAGE_STORAGE_AND_WINRT=PASS"
}
finally {
    if ($process -and -not $process.HasExited) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }
    if ($installed) {
        Write-Host "==> Removendo pacote de teste"
        Remove-AppxPackage -Package $installed.PackageFullName -ErrorAction SilentlyContinue
    }
    if ($certificate.Thumbprint) {
        Remove-Item -Path (Join-Path $trustedStore $certificate.Thumbprint) -Force -ErrorAction SilentlyContinue
    }
}
