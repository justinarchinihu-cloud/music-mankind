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

if (!sceneContainer) {
    console.error("❌ Missing #scene-container in HTML");
    return;
}

if (!window.THREE) {
    console.error("❌ Three.js not loaded");
    return;
}

/* =========================
   REGION DATA
========================= */

const regions = {
    europe: { lat: 50, lon: 10, tag: "jazz" },
    northamerica: { lat: 40, lon: -100, tag: "rock" },
    asia: { lat: 30, lon: 100, tag: "pop" },
    africa: { lat: 0, lon: 20, tag: "afrobeat" },
    southamerica: { lat: -15, lon: -60, tag: "latin" },
    oceania: { lat: -25, lon: 135, tag: "electronic" }
};

/* =========================
   RADIO SYSTEM
========================= */

function loadRegion(regionKey) {

    const region = regions[regionKey];
    if (!region) return;

    regionTitle.textContent = regionKey.toUpperCase();

    fetch(`https://de1.api.radio-browser.info/json/stations/bytag/${region.tag}`)
        .then(res => res.json())
        .then(data => renderStations(data.slice(0, 12)))
        .catch(err => console.error("API error:", err));
}

function renderStations(stations) {

    stationsDiv.innerHTML = "";

    stations.forEach(station => {

        const btn = document.createElement("button");
        btn.textContent = station.name;

        btn.onclick = () => {

            radioAudio.pause();
            radioAudio.src = station.url_resolved;

            radioAudio.play().catch(err => {
                console.error("Playback error:", err);
            });
        };

        stationsDiv.appendChild(btn);
    });
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

const renderer = new THREE.WebGLRenderer({ antialias: true });

/* FIXED SIZE */
const size = 450;
renderer.setSize(size, size);

sceneContainer.appendChild(renderer.domElement);

/* =========================
   LIGHTING
========================= */

const light = new THREE.DirectionalLight(0xffffff, 1.5);
light.position.set(5, 3, 5);
scene.add(light);

/* =========================
   EARTH
========================= */

const earth = new THREE.Mesh(
    new THREE.SphereGeometry(2.5, 64, 64),
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

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener("click", (event) => {

    const rect = renderer.domElement.getBoundingClientRect();

    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);

    const hits = raycaster.intersectObject(earth);

    if (!hits.length) return;

    /* SIMPLE REGION PICK (STABLE VERSION) */
    const keys = Object.keys(regions);
    const selected = keys[Math.floor(Math.random() * keys.length)];

    loadRegion(selected);
});

/* =========================
   ANIMATION LOOP
========================= */

function animate() {

    requestAnimationFrame(animate);

    earth.rotation.y += 0.003;

    renderer.render(scene, camera);
}

animate();

}); 