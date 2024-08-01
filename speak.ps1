$speechSynthesizer = New-Object -TypeName System.Speech.Synthesis.SpeechSynthesizer
$soundFilePath = "Test.wav"
try {
    
    $Location = "output.txt"
    $Destination = "output.wav"

    # $speechSynthesizer.SetOutputToWaveFile($soundFilePath)
    $Contents = Get-Content $Location
    $speechSynthesizer.Speak($Contents)
}
finally {
    if ($speechSynthesizer) {
        $speechSynthesizer.Dispose()
    }
}