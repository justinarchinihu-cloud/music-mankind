const songCards = document.querySelectorAll(".visualizer-song-card");
const dropZone = document.getElementById("dropZone");

const audioPlayer = document.getElementById("audioPlayer");

const currentSongCover = document.getElementById("currentSongCover");
const currentSongTitle = document.getElementById("currentSongTitle");
const currentSongArtist = document.getElementById("currentSongArtist");
const currentSongAlbum = document.getElementById("currentSongAlbum");

const bassSlider = document.getElementById("bass");
const midSlider = document.getElementById("mid");
const trebleSlider = document.getElementById("treble");

const bassValue = document.getElementById("bassValue");
const midValue = document.getElementById("midValue");
const trebleValue = document.getElementById("trebleValue");

const canvas = document.getElementById("visualizer");
const canvasContext = canvas.getContext("2d");

let audioContext;
let source;
let analyser;
let bassFilter;
let midFilter;
let trebleFilter;
let animationId;
let currentPreviewAlertShown = false;

function resizeCanvas() {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}

resizeCanvas();
window.addEventListener("resize", resizeCanvas);

function setupAudioContext() {
    if (!audioContext) {
        audioContext = new AudioContext();

        source = audioContext.createMediaElementSource(audioPlayer);

        bassFilter = audioContext.createBiquadFilter();
        bassFilter.type = "lowshelf";
        bassFilter.frequency.value = 200;
        bassFilter.gain.value = 0;

        midFilter = audioContext.createBiquadFilter();
        midFilter.type = "peaking";
        midFilter.frequency.value = 1000;
        midFilter.Q.value = 1;
        midFilter.gain.value = 0;

        trebleFilter = audioContext.createBiquadFilter();
        trebleFilter.type = "highshelf";
        trebleFilter.frequency.value = 3000;
        trebleFilter.gain.value = 0;

        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;

        source
            .connect(bassFilter)
            .connect(midFilter)
            .connect(trebleFilter)
            .connect(analyser)
            .connect(audioContext.destination);
    }

    if (audioContext.state === "suspended") {
        audioContext.resume();
    }
}

function loadSong(card) {
    const songSrc = card.dataset.src;
    const songTitle = card.dataset.title;
    const songArtist = card.dataset.artist;
    const songAlbum = card.dataset.album;
    const songCover = card.dataset.cover;

    audioPlayer.src = songSrc;
    audioPlayer.currentTime = 0;
    currentPreviewAlertShown = false;

    currentSongCover.src = songCover;
    currentSongTitle.textContent = songTitle;
    currentSongArtist.textContent = songArtist;
    currentSongAlbum.textContent = songAlbum;

    setupAudioContext();

    audioPlayer.play();

    drawVisualizer();
}

songCards.forEach((card) => {
    card.addEventListener("dragstart", (event) => {
        event.dataTransfer.setData("text/plain", card.dataset.title);
        card.classList.add("dragging");
    });

    card.addEventListener("dragend", () => {
        card.classList.remove("dragging");
    });

    card.addEventListener("click", () => {
        loadSong(card);
    });
});

dropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", (event) => {
    event.preventDefault();

    dropZone.classList.remove("drag-over");

    const draggedTitle = event.dataTransfer.getData("text/plain");

    const matchingCard = Array.from(songCards).find(
        (card) => card.dataset.title === draggedTitle
    );

    if (matchingCard) {
        loadSong(matchingCard);
    }
});

if (bassSlider) {
    bassSlider.addEventListener("input", () => {
        bassFilter.gain.value = bassSlider.value;
        bassValue.textContent = `${bassSlider.value} dB`;
    });
}

if (midSlider) {
    midSlider.addEventListener("input", () => {
        midFilter.gain.value = midSlider.value;
        midValue.textContent = `${midSlider.value} dB`;
    });
}

if (trebleSlider) {
    trebleSlider.addEventListener("input", () => {
        trebleFilter.gain.value = trebleSlider.value;
        trebleValue.textContent = `${trebleSlider.value} dB`;
    });
}

audioPlayer.addEventListener("play", () => {
    setupAudioContext();
    drawVisualizer();
});

audioPlayer.addEventListener("timeupdate", () => {
    if (!isAuthenticated && audioPlayer.currentTime >= 7) {
        audioPlayer.pause();
        audioPlayer.currentTime = 0;

        if (!currentPreviewAlertShown) {
            currentPreviewAlertShown = true;

            alert("Preview ended. Login or create an account for full playback.");
        }
    }
});

audioPlayer.addEventListener("ended", () => {
    cancelAnimationFrame(animationId);
});

function drawVisualizer() {
    if (!analyser) return;

    animationId = requestAnimationFrame(drawVisualizer);

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    analyser.getByteFrequencyData(dataArray);

    canvasContext.clearRect(0, 0, canvas.width, canvas.height);

    const barWidth = canvas.width / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
        const barHeight = dataArray[i];

        canvasContext.fillStyle = "white";
        canvasContext.fillRect(
            x,
            canvas.height - barHeight,
            barWidth - 2,
            barHeight
        );

        x += barWidth;
    }
}