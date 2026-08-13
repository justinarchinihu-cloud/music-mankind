document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       ELEMENTS
    ========================= */

    const songCards = document.querySelectorAll(".visualizer-song-card");
    const dropZone = document.getElementById("dropZone");

    const audioPlayer = document.getElementById("audioPlayer");

    const currentSongCover =
        document.getElementById("currentSongCover");

    const currentSongTitle =
        document.getElementById("currentSongTitle");

    const currentSongArtist =
        document.getElementById("currentSongArtist");

    const currentSongAlbum =
        document.getElementById("currentSongAlbum");


    /* =========================
       EQ CONTROLS
    ========================= */

    const bassSlider =
        document.getElementById("bass");

    const midSlider =
        document.getElementById("mid");

    const trebleSlider =
        document.getElementById("treble");


    const bassValue =
        document.getElementById("bassValue");

    const midValue =
        document.getElementById("midValue");

    const trebleValue =
        document.getElementById("trebleValue");


    /* =========================
       VISUALIZER
    ========================= */

    const canvas =
        document.getElementById("visualizer");


    if (!audioPlayer || !canvas) {
        console.error(
            "Audio player or visualizer canvas is missing."
        );

        return;
    }


    const canvasContext =
        canvas.getContext("2d");


    /* =========================
       AUTHENTICATION
    ========================= */

    const isAuthenticated =
        window.isAuthenticated === true;


    /* =========================
       AUDIO VARIABLES
    ========================= */

    let audioContext = null;

    let source = null;

    let analyser = null;

    let bassFilter = null;

    let midFilter = null;

    let trebleFilter = null;

    let animationId = null;

    let currentPreviewAlertShown = false;


    /* =========================
       CANVAS RESIZE
    ========================= */

    function resizeCanvas() {

        canvas.width =
            canvas.offsetWidth || 800;

        canvas.height =
            canvas.offsetHeight || 300;

    }


    resizeCanvas();


    window.addEventListener(
        "resize",
        resizeCanvas
    );


    /* =========================
       AUDIO CONTEXT
    ========================= */

    function setupAudioContext() {

        if (!audioContext) {

            const AudioContext =
                window.AudioContext ||
                window.webkitAudioContext;


            if (!AudioContext) {

                console.error(
                    "Web Audio API is not supported."
                );

                return false;
            }


            audioContext =
                new AudioContext();


            source =
                audioContext.createMediaElementSource(
                    audioPlayer
                );


            /* =========================
               BASS
            ========================= */

            bassFilter =
                audioContext.createBiquadFilter();

            bassFilter.type =
                "lowshelf";

            bassFilter.frequency.value =
                200;

            bassFilter.gain.value =
                0;


            /* =========================
               MID
            ========================= */

            midFilter =
                audioContext.createBiquadFilter();

            midFilter.type =
                "peaking";

            midFilter.frequency.value =
                1000;

            midFilter.Q.value =
                1;

            midFilter.gain.value =
                0;


            /* =========================
               TREBLE
            ========================= */

            trebleFilter =
                audioContext.createBiquadFilter();

            trebleFilter.type =
                "highshelf";

            trebleFilter.frequency.value =
                3000;

            trebleFilter.gain.value =
                0;


            /* =========================
               ANALYSER
            ========================= */

            analyser =
                audioContext.createAnalyser();

            analyser.fftSize =
                256;


            /* =========================
               AUDIO CHAIN
            ========================= */

            source
                .connect(bassFilter)
                .connect(midFilter)
                .connect(trebleFilter)
                .connect(analyser)
                .connect(audioContext.destination);

        }


        if (
            audioContext &&
            audioContext.state === "suspended"
        ) {

            audioContext.resume();

        }


        return true;

    }


    /* =========================
       LOAD SONG
    ========================= */

    function loadSong(card) {

        if (!card) {
            return;
        }


        const songSrc =
            card.dataset.src;

        const songTitle =
            card.dataset.title || "Unknown Title";

        const songArtist =
            card.dataset.artist || "Unknown Artist";

        const songAlbum =
            card.dataset.album || "Unknown Album";

        const songCover =
            card.dataset.cover || "";


        if (!songSrc) {

            console.error(
                "Song does not have a data-src:",
                card
            );

            return;
        }


        /* =========================
           STOP CURRENT AUDIO
        ========================= */

        audioPlayer.pause();


        cancelAnimationFrame(
            animationId
        );


        /* =========================
           LOAD NEW SONG
        ========================= */

        audioPlayer.src =
            songSrc;

        audioPlayer.currentTime =
            0;

        audioPlayer.load();


        currentPreviewAlertShown =
            false;


        /* =========================
           UPDATE UI
        ========================= */

        if (currentSongCover) {

            currentSongCover.src =
                songCover;

        }


        if (currentSongTitle) {

            currentSongTitle.textContent =
                songTitle;

        }


        if (currentSongArtist) {

            currentSongArtist.textContent =
                songArtist;

        }


        if (currentSongAlbum) {

            currentSongAlbum.textContent =
                songAlbum;

        }


        /* =========================
           START AUDIO
        ========================= */

        if (!setupAudioContext()) {
            return;
        }


        audioPlayer
            .play()
            .then(() => {

                drawVisualizer();

            })
            .catch((error) => {

                console.error(
                    "Playback error:",
                    error
                );

            });

    }


    /* =========================
       SONG CARD CLICK
    ========================= */

    songCards.forEach((card) => {

        card.addEventListener(
            "click",
            () => {

                loadSong(card);

            }
        );


        /* =========================
           DRAG START
        ========================= */

        card.addEventListener(
            "dragstart",
            (event) => {

                event.dataTransfer.setData(
                    "text/plain",
                    card.dataset.title || ""
                );


                card.classList.add(
                    "dragging"
                );

            }
        );


        /* =========================
           DRAG END
        ========================= */

        card.addEventListener(
            "dragend",
            () => {

                card.classList.remove(
                    "dragging"
                );

            }
        );

    });


    /* =========================
       DROP ZONE
    ========================= */

    if (dropZone) {

        dropZone.addEventListener(
            "dragover",
            (event) => {

                event.preventDefault();

                dropZone.classList.add(
                    "drag-over"
                );

            }
        );


        dropZone.addEventListener(
            "dragleave",
            () => {

                dropZone.classList.remove(
                    "drag-over"
                );

            }
        );


        dropZone.addEventListener(
            "drop",
            (event) => {

                event.preventDefault();

                dropZone.classList.remove(
                    "drag-over"
                );


                const draggedTitle =
                    event.dataTransfer.getData(
                        "text/plain"
                    );


                const matchingCard =
                    Array.from(songCards).find(
                        (card) =>
                            card.dataset.title ===
                            draggedTitle
                    );


                if (matchingCard) {

                    loadSong(
                        matchingCard
                    );

                }

            }
        );

    }


    /* =========================
       BASS
    ========================= */

    if (bassSlider) {

        bassSlider.addEventListener(
            "input",
            () => {

                if (!bassFilter) {
                    setupAudioContext();
                }


                if (bassFilter) {

                    bassFilter.gain.value =
                        Number(
                            bassSlider.value
                        );

                }


                if (bassValue) {

                    bassValue.textContent =
                        `${bassSlider.value} dB`;

                }

            }
        );

    }


    /* =========================
       MID
    ========================= */

    if (midSlider) {

        midSlider.addEventListener(
            "input",
            () => {

                if (!midFilter) {
                    setupAudioContext();
                }


                if (midFilter) {

                    midFilter.gain.value =
                        Number(
                            midSlider.value
                        );

                }


                if (midValue) {

                    midValue.textContent =
                        `${midSlider.value} dB`;

                }

            }
        );

    }


    /* =========================
       TREBLE
    ========================= */

    if (trebleSlider) {

        trebleSlider.addEventListener(
            "input",
            () => {

                if (!trebleFilter) {
                    setupAudioContext();
                }


                if (trebleFilter) {

                    trebleFilter.gain.value =
                        Number(
                            trebleSlider.value
                        );

                }


                if (trebleValue) {

                    trebleValue.textContent =
                        `${trebleSlider.value} dB`;

                }

            }
        );

    }


    /* =========================
       PLAY EVENT
    ========================= */

    audioPlayer.addEventListener(
        "play",
        () => {

            if (!setupAudioContext()) {
                return;
            }


            drawVisualizer();

        }
    );


    /* =========================
       PREVIEW LIMIT
    ========================= */

    audioPlayer.addEventListener(
        "timeupdate",
        () => {

            if (
                !isAuthenticated &&
                audioPlayer.currentTime >= 7
            ) {

                audioPlayer.pause();

                audioPlayer.currentTime =
                    0;


                if (
                    !currentPreviewAlertShown
                ) {

                    currentPreviewAlertShown =
                        true;


                    alert(
                        "Preview ended. Login or create an account for full playback."
                    );

                }

            }

        }
    );


    /* =========================
       AUDIO ENDED
    ========================= */

    audioPlayer.addEventListener(
        "ended",
        () => {

            cancelAnimationFrame(
                animationId
            );

        }
    );


    /* =========================
       VISUALIZER
    ========================= */

    function drawVisualizer() {

        if (!analyser) {
            return;
        }


        animationId =
            requestAnimationFrame(
                drawVisualizer
            );


        const bufferLength =
            analyser.frequencyBinCount;


        const dataArray =
            new Uint8Array(
                bufferLength
            );


        analyser.getByteFrequencyData(
            dataArray
        );


        canvasContext.clearRect(
            0,
            0,
            canvas.width,
            canvas.height
        );


        const barWidth =
            canvas.width /
            bufferLength;


        let x = 0;


        for (
            let i = 0;
            i < bufferLength;
            i++
        ) {

            const barHeight =
                dataArray[i];


            canvasContext.fillStyle =
                "white";


            canvasContext.fillRect(
                x,
                canvas.height - barHeight,
                Math.max(
                    barWidth - 2,
                    1
                ),
                barHeight
            );


            x += barWidth;

        }

    }

});