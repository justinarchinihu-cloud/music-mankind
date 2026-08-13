document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       ELEMENTS
    ========================= */

    const stationsDiv = document.getElementById("stations");
    const radioAudio = document.getElementById("radioAudio");
    const regionTitle = document.getElementById("regionTitle");
    const sceneContainer = document.getElementById("scene-container");


    /* =========================
       SAFETY CHECKS
    ========================= */

    if (!stationsDiv || !radioAudio || !regionTitle || !sceneContainer) {
        console.error("Radio HTML elements are missing.");
        return;
    }

    if (!window.THREE) {
        console.error("Three.js not loaded.");
        return;
    }


    /* =========================
       REGION DATA
    ========================= */

    const regions = {

        europe: {
            lat: 50,
            lon: 10,
            tag: "jazz"
        },

        northamerica: {
            lat: 40,
            lon: -100,
            tag: "rock"
        },

        asia: {
            lat: 30,
            lon: 100,
            tag: "pop"
        },

        africa: {
            lat: 0,
            lon: 20,
            tag: "afrobeat"
        },

        southamerica: {
            lat: -15,
            lon: -60,
            tag: "latin"
        },

        oceania: {
            lat: -25,
            lon: 135,
            tag: "electronic"
        }

    };


    /* =========================
       RADIO API SERVERS
    ========================= */

    const radioServers = [

        "https://de1.api.radio-browser.info",

        "https://nl1.api.radio-browser.info",

        "https://at1.api.radio-browser.info"

    ];


    /* =========================
       LOAD REGION
    ========================= */

    async function loadRegion(regionKey) {

        const region = regions[regionKey];

        if (!region) {
            console.error("Unknown region:", regionKey);
            return;
        }

        regionTitle.textContent =
            regionKey.charAt(0).toUpperCase() +
            regionKey.slice(1);

        stationsDiv.innerHTML = `
            <p class="radio-status">
                Loading ${region.tag} stations...
            </p>
        `;


        let stations = null;


        for (const server of radioServers) {

            try {

                const response = await fetch(
                    `${server}/json/stations/bytag/${encodeURIComponent(region.tag)}?limit=20&hidebroken=true`
                );


                if (!response.ok) {
                    throw new Error(
                        `HTTP ${response.status}`
                    );
                }


                const data = await response.json();

                if (Array.isArray(data) && data.length > 0) {

                    stations = data;

                    break;

                }

            } catch (error) {

                console.warn(
                    `Radio server failed: ${server}`,
                    error
                );

            }

        }


        if (!stations || stations.length === 0) {

            stationsDiv.innerHTML = `
                <p class="radio-status">
                    No stations could be loaded right now.
                </p>
            `;

            return;
        }


        renderStations(stations.slice(0, 12));

    }


    /* =========================
       RENDER STATIONS
    ========================= */

    function renderStations(stations) {

        stationsDiv.innerHTML = "";


        stations.forEach((station) => {

            if (!station.url_resolved) {
                return;
            }


            const btn = document.createElement("button");

            btn.type = "button";

            btn.className = "radio-station";

            btn.textContent =
                station.name || "Unknown Station";


            btn.addEventListener("click", async () => {

                await playStation(
                    station.url_resolved,
                    station.name
                );

            });


            stationsDiv.appendChild(btn);

        });


        if (!stationsDiv.children.length) {

            stationsDiv.innerHTML = `
                <p class="radio-status">
                    No playable stations found.
                </p>
            `;

        }

    }


    /* =========================
       PLAY STATION
    ========================= */

    async function playStation(url, stationName) {

        if (!url) {
            return;
        }


        try {

            radioAudio.pause();

            radioAudio.removeAttribute("src");

            radioAudio.load();

            radioAudio.src = url;

            radioAudio.load();


            await radioAudio.play();


            regionTitle.textContent =
                stationName || "Music Mankind Radio";


        } catch (error) {

            console.error(
                "Radio playback error:",
                error
            );

            regionTitle.textContent =
                "Unable to play station";

        }

    }


    /* =========================
       THREE.JS SETUP
    ========================= */

    const scene = new THREE.Scene();


    const camera = new THREE.PerspectiveCamera(
        75,
        1,
        0.1,
        1000
    );


    const renderer =
        new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });


    /* =========================
       RESPONSIVE GLOBE SIZE
    ========================= */

    function getGlobeSize() {

        const width =
            sceneContainer.clientWidth || 450;

        return Math.min(width, 450);

    }


    function resizeGlobe() {

        const size = getGlobeSize();

        renderer.setSize(
            size,
            size
        );


        camera.aspect = 1;

        camera.updateProjectionMatrix();

    }


    sceneContainer.appendChild(
        renderer.domElement
    );


    resizeGlobe();

    window.addEventListener(
        "resize",
        resizeGlobe
    );


    /* =========================
       LIGHTING
    ========================= */

    const light =
        new THREE.DirectionalLight(
            0xffffff,
            1.5
        );


    light.position.set(
        5,
        3,
        5
    );


    scene.add(light);


    /* =========================
       EARTH
    ========================= */

    const earth =
        new THREE.Mesh(

            new THREE.SphereGeometry(
                2.5,
                64,
                64
            ),

            new THREE.MeshStandardMaterial({

                color: 0x111111,

                wireframe: true

            })

        );


    scene.add(earth);


    camera.position.z = 6;


    /* =========================
       CLICK SYSTEM
    ========================= */

    const raycaster =
        new THREE.Raycaster();


    const mouse =
        new THREE.Vector2();


    renderer.domElement.addEventListener(
        "click",
        (event) => {

            const rect =
                renderer.domElement
                    .getBoundingClientRect();


            mouse.x =
                ((event.clientX - rect.left)
                    / rect.width) * 2 - 1;


            mouse.y =
                -((event.clientY - rect.top)
                    / rect.height) * 2 + 1;


            raycaster.setFromCamera(
                mouse,
                camera
            );


            const hits =
                raycaster.intersectObject(
                    earth
                );


            if (!hits.length) {
                return;
            }


            const keys =
                Object.keys(regions);


            const selected =
                keys[
                    Math.floor(
                        Math.random() *
                        keys.length
                    )
                ];


            loadRegion(selected);

        }
    );


    /* =========================
       ANIMATION
    ========================= */

    function animate() {

        requestAnimationFrame(
            animate
        );


        earth.rotation.y += 0.003;


        renderer.render(
            scene,
            camera
        );

    }


    animate();


    /* =========================
       INITIAL STATIONS
    ========================= */

    loadRegion("northamerica");

});