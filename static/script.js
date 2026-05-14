const audioPlayers = document.querySelectorAll("audio");

audioPlayers.forEach((audio) => {
    audio.addEventListener("play", () => {
        audioPlayers.forEach((otherAudio) => {
            if (otherAudio !== audio) {
                otherAudio.pause();
                otherAudio.currentTime = otherAudio.currentTime;
            }
        });
    });
});