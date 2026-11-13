<#
.SYNOPSIS  Gera exclusivamente o pacote MSIX para Microsoft Store.
.EXAMPLE   ./packaging/build.ps1 -IdentityName "12345Publisher.StartupMessage" -Publisher "CN=XXXXXXXX-XXXX" -PublisherDisplayName "Seu Nome"
.EXAMPLE   ./packaging/build.ps1 -SignTest   # MSIX assinado com certificado de teste (instalação local)
#>
[CmdletBinding()]
param(
  [string]$Version,
  [switch]$SignTest,
  [string]$IdentityName = "Publisher.StartupMessage",
  [string]$Publisher = "CN=Publisher",
  [string]$PublisherDisplayName = "Publisher",
  [string]$DisplayName = "StartupMessage"
)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $root

function Find-SdkTool([string]$name) {
  $bin = Join-Path ${env:ProgramFiles(x86)} "Windows Kits\10\bin"
  $dirs = Get-ChildItem $bin -Directory -ErrorAction SilentlyContinue |
          Where-Object Name -Match '^10\.' | Sort-Object Name -Descending
  foreach ($d in $dirs) {
    $p = Join-Path $d.FullName "x64\$name"
    if (Test-Path $p) { return $p }
  }
  throw "$name não encontrado. Instale o Windows 10/11 SDK."
}

if (-not $Version) {
  $m = Select-String -Path "src/dailymessage/__init__.py" -Pattern '__version__\s*=\s*"([^"]+)"'
  $Version = $m.Matches[0].Groups[1].Value
}
Write-Host "==> StartupMessage MSIX — versão $Version"
if ($IdentityName -eq "Publisher.StartupMessage" -or $Publisher -eq "CN=Publisher") { Write-Warning "Identidade provisória: pacote apenas para validação, não submeta à Store." }

Write-Host "==> Gerando ícones (placeholders, se ainda não existirem)"
python packaging/make_assets.py

Write-Host "==> PyInstaller"
foreach ($d in "build", "dist", "release") { if (Test-Path $d) { Remove-Item $d -Recurse -Force } }
python -m PyInstaller packaging/dailymessage.spec --noconfirm --clean --distpath dist --workpath build/pyi
if ($LASTEXITCODE -ne 0) { throw "PyInstaller falhou" }

$release = Join-Path $root "release"
New-Item -ItemType Directory -Force $release | Out-Null

  Write-Host "==> Empacotando MSIX"
  $makeappx = Find-SdkTool "makeappx.exe"
  $stage = Join-Path $root "build/msix"
  if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
  New-Item -ItemType Directory -Force $stage | Out-Null
  Copy-Item "dist/StartupMessage/*" $stage -Recurse
  Copy-Item "packaging/Assets" (Join-Path $stage "Assets") -Recurse

  $parts = @($Version.Split('.')); while ($parts.Count -lt 3) { $parts += '0' }
  $msixVersion = ($parts[0..2] -join '.') + '.0'   # a Store exige o 4º número = 0

  $manifest = Get-Content "packaging/AppxManifest.xml" -Raw -Encoding UTF8
  $manifest = $manifest.Replace("{{IDENTITY_NAME}}", $IdentityName).Replace("{{PUBLISHER}}", $Publisher).
    Replace("{{PUBLISHER_DISPLAY_NAME}}", $PublisherDisplayName).Replace("{{DISPLAY_NAME}}", $DisplayName).
    Replace("{{VERSION}}", $msixVersion)
  Set-Content (Join-Path $stage "AppxManifest.xml") $manifest -Encoding UTF8

  $out = Join-Path $release "StartupMessage_${msixVersion}_x64.msix"
  & $makeappx pack /d $stage /p $out /o
  if ($LASTEXITCODE -ne 0) { throw "makeappx falhou" }
  Write-Host "   $out"

  if ($SignTest) {
    Write-Host "==> Assinatura de TESTE (não use para a Store)"
    $signtool = Find-SdkTool "signtool.exe"
    $cert = New-SelfSignedCertificate -Type Custom -Subject $Publisher -KeyUsage DigitalSignature `
      -FriendlyName "StartupMessage Test" -CertStoreLocation "Cert:\CurrentUser\My" `
      -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
    $pfx = Join-Path $release "StartupMessage-test.pfx"
    $cer = Join-Path $release "StartupMessage-test.cer"
    Export-PfxCertificate -Cert $cert -FilePath $pfx -Password (ConvertTo-SecureString "test1234" -AsPlainText -Force) | Out-Null
    Export-Certificate -Cert $cert -FilePath $cer | Out-Null
    $testOut = Join-Path $release "StartupMessage-validation.msix"
    Copy-Item $out $testOut -Force
    & $signtool sign /fd SHA256 /f $pfx /p test1234 $testOut
    if ($LASTEXITCODE -ne 0) { throw "Assinatura de teste falhou" }
    # A verificação da confiança ocorre no teste de instalação, após importar o certificado em TrustedPeople.
    Write-Host "   Pacote de validação assinado: $testOut"
    Write-Host "   Pacote de envio à Store (não assinado): $out"
  }
Write-Host "==> Pacote MSIX concluído."
