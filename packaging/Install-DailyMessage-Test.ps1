[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$msixPath = Join-Path $PSScriptRoot "StartupMessage-validation.msix"
$certificatePath = Join-Path $PSScriptRoot "StartupMessage-test.cer"

if (-not (Test-Path $msixPath)) {
    throw "Arquivo StartupMessage-validation.msix não foi encontrado na mesma pasta deste instalador."
}
if (-not (Test-Path $certificatePath)) {
    throw "Certificado StartupMessage-test.cer não foi encontrado na mesma pasta deste instalador."
}

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "O certificado de teste precisa ser confiado pelo computador. O Windows solicitará autorização de administrador." -ForegroundColor Yellow
    $arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + $PSCommandPath + '"'
    $elevated = Start-Process -FilePath "powershell.exe" -Verb RunAs -ArgumentList $arguments -Wait -PassThru
    exit $elevated.ExitCode
}

Write-Host "==> Conferindo certificado público do pacote..."
$certificate = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($certificatePath)
if ($certificate.HasPrivateKey) {
    throw "O arquivo .cer deveria conter somente a chave pública, sem chave privada."
}

$signature = Get-AuthenticodeSignature -FilePath $msixPath
if (-not $signature.SignerCertificate) {
    throw "Não foi possível identificar o certificado que assinou o MSIX."
}
if ($signature.SignerCertificate.Thumbprint -ne $certificate.Thumbprint) {
    throw "O certificado fornecido não corresponde à assinatura deste pacote MSIX."
}

Write-Host "==> Adicionando certificado a Computador Local > Pessoas Confiáveis..."
$storePath = "Cert:\LocalMachine\TrustedPeople"
$existing = Get-ChildItem $storePath | Where-Object Thumbprint -EQ $certificate.Thumbprint
if (-not $existing) {
    Import-Certificate -FilePath $certificatePath -CertStoreLocation $storePath | Out-Null
}

Write-Host "==> Instalando StartupMessage..."
Add-AppxPackage -Path $msixPath -ErrorAction Stop

Write-Host ""
Write-Host "StartupMessage foi instalado com sucesso." -ForegroundColor Green
Write-Host "Abra o aplicativo pelo menu Iniciar."
Write-Host "O certificado público permanecerá em Pessoas Confiáveis para futuras atualizações deste build."
Write-Host ""
Read-Host "Pressione Enter para fechar"
