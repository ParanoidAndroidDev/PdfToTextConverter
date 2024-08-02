$speechSynthesizer = New-Object -TypeName System.Speech.Synthesis.SpeechSynthesizer
try {
    
    $Location = "output.txt"
    $Destination = "D:\sebi_\projects\PdfToTextConverter\output.wav"

    $streamFormat = [System.Speech.AudioFormat.SpeechAudioFormatInfo]::new(8000,[System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen,[System.Speech.AudioFormat.AudioChannel]::Mono)
    $speechSynthesizer.SetOutputToWaveFile($Destination, $streamFormat)
    $Contents = Get-Content $Location
    $speechSynthesizer.Speak($Contents)
}
finally {
    if ($speechSynthesizer) {
        $speechSynthesizer.Dispose()
    }
}