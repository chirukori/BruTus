/**
 * BruTus Health • Interactive 3D Anatomical Human Eye
 * Built with Three.js: Realistic anatomical proportions, procedural textures,
 * exploded-view animation, layer raycasting, and Diabetic Retinopathy clinical callout.
 */

(function () {
    'use strict';

    // Anatomical Structures Metadata
    const ANATOMY_DATA = {
        'cornea': {
            name: 'Cornea',
            category: 'Anterior Refractive Tunic',
            description: 'The transparent anterior dome of the eye covering the iris and pupil. It provides roughly two-thirds of the total optical refractive power, directing photons into the crystalline lens.',
            clinical: 'Corneal clarity is vital for visual acuity. Diabetic autonomic neuropathy can impair corneal epithelial nerve density and delay wound healing.'
        },
        'iris': {
            name: 'Iris',
            category: 'Anterior Uvea / Muscular Diaphragm',
            description: 'Pigmented muscular contractile disc regulating pupillary diameter through the sphincter and dilator pupillae muscles, controlling intraocular illumination.',
            clinical: 'In advanced proliferative diabetic retinopathy, severe ischemia can trigger neovascularization of the iris (rubeosis iridis), leading to secondary neovascular glaucoma.'
        },
        'pupil': {
            name: 'Pupil',
            category: 'Optical Aperture',
            description: 'The central circular aperture in the iris that dilates (mydriasis) and constricts (miosis) to regulate incoming light flux entering the posterior segment.',
            clinical: 'Pharmacological pupillary dilation is the clinical prerequisite for funduscopy and AI-assisted diabetic retinopathy fundus screening.'
        },
        'lens': {
            name: 'Crystalline Lens',
            category: 'Dynamic Accommodation Element',
            description: 'A flexible, biconvex crystalline structure suspended behind the pupil. Ciliary muscle contraction dynamically modulates curvature to bring near and distant objects into sharp focus.',
            clinical: 'Hyperglycemia causes osmotic accumulation of sorbitol via the polyol pathway, causing acute myopic refractive shifts and accelerated diabetic cataractogenesis.'
        },
        'retina': {
            name: 'Retina',
            category: 'Neurosensory Tunic ★ PRIMARY DR TARGET',
            description: 'The light-sensitive neurosensory layer lining the posterior eye. Ten distinct micro-layers of photoreceptors (rods and cones) convert light photons into neural action potentials.',
            clinical: 'DIABETIC RETINOPATHY TARGET: Chronic elevated blood glucose destroys retinal capillary pericytes, causing microaneurysms, hemorrhages, hard lipid exudates, macular edema, and vision-threatening neovascularization.'
        },
        'choroid': {
            name: 'Choroid',
            category: 'Vascular Middle Uveal Tunic',
            description: 'The highly vascular, pigmented layer located between the retina and sclera. The choriocapillaris delivers dense blood flow, oxygen, and metabolic nutrients to the outer retinal layers.',
            clinical: 'Diabetic choroidopathy causes focal choriocapillaris non-perfusion and vascular drop-out, compounding outer retinal hypoxia and accelerating neurodegeneration.'
        },
        'sclera': {
            name: 'Sclera',
            category: 'Fibrous Protective Outer Tunic',
            description: 'The opaque, protective outer layer composed of dense collagenous fibers. It maintains intraocular pressure, ocular volume, and structural shape, anchoring the extraocular muscles.',
            clinical: 'Maintains ocular structural integrity and resists tensile intraocular stresses, protecting internal delicate sensory and vascular tunics.'
        },
        'optic_nerve': {
            name: 'Optic Nerve (CN II)',
            category: 'Central Visual Pathway',
            description: 'A bundle of over one million myelinated retinal ganglion cell axons exiting through the lamina cribrosa, transmitting visual impulses to the lateral geniculate nucleus and visual cortex.',
            clinical: 'Neovascularization at the Optic Disc (NVD) represents one of the highest-risk indicators of proliferative diabetic retinopathy, requiring urgent retinal laser photocoagulation or anti-VEGF therapy.'
        }
    };

    // Layer-specific tailored emissive highlights (prevents color bleaching)
    const LAYER_EMISSIVE_CONFIG = {
        'retina': { color: 0xef4444, intensity: 0.35 },    // Crimson/ruby glow for retina
        'iris': { color: 0x0ea5e9, intensity: 0.35 },      // Sapphire blue glow for iris
        'pupil': { color: 0x1e293b, intensity: 0.2 },
        'cornea': { color: 0x38bdf8, intensity: 0.25 },    // Ice-blue glow for cornea
        'lens': { color: 0x60a5fa, intensity: 0.3 },       // Translucent blue glow for lens
        'choroid': { color: 0x991b1b, intensity: 0.3 },    // Deep vascular red glow for choroid
        'sclera': { color: 0x10b981, intensity: 0.2 },     // Emerald accent for sclera
        'optic_nerve': { color: 0xfacc15, intensity: 0.3 } // Warm amber-golden glow for optic nerve
    };

    // Helper: Generate procedural Sclera texture with natural ivory tone and fine ciliary micro-vessels
    function createScleraTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 1024;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');

        // Natural off-white / porcelain base (not blown-out pure white)
        const grad = ctx.createLinearGradient(0, 0, 1024, 512);
        grad.addColorStop(0, '#ede7df');
        grad.addColorStop(0.35, '#e4ded4');
        grad.addColorStop(0.7, '#ded7cc');
        grad.addColorStop(1, '#e8e2d8');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 1024, 512);

        // Delicate ciliary micro-vasculature (fine red ciliary blood vessel filaments)
        ctx.lineWidth = 1.0;
        for (let i = 0; i < 50; i++) {
            ctx.strokeStyle = Math.random() > 0.5 ? 'rgba(185, 28, 28, 0.55)' : 'rgba(225, 29, 72, 0.4)';
            ctx.beginPath();
            let x = Math.random() * 1024;
            let y = Math.random() * 512;
            ctx.moveTo(x, y);
            const segments = 4 + Math.floor(Math.random() * 5);
            for (let j = 0; j < segments; j++) {
                x += (Math.random() - 0.48) * 45;
                y += (Math.random() - 0.5) * 35;
                ctx.lineTo(x, y);
            }
            ctx.stroke();
        }

        const texture = new THREE.CanvasTexture(canvas);
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.ClampToEdgeWrapping;
        return texture;
    }

    // Helper: Generate procedural Iris texture with realistic blue/hazel stroma fibers and dark limbal ring
    function createIrisTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');
        const cx = 256, cy = 256;

        // Base gradient: Dark limbal ring -> rich sapphire blue -> teal hazel -> golden collarette
        const radGrad = ctx.createRadialGradient(cx, cy, 35, cx, cy, 250);
        radGrad.addColorStop(0, '#020b12');
        radGrad.addColorStop(0.18, '#854d0e'); // Inner pupillary zone (golden hazel)
        radGrad.addColorStop(0.35, '#0d9488'); // Mid-stroma transition (teal)
        radGrad.addColorStop(0.65, '#0284c7'); // Outer stroma (rich ocean blue)
        radGrad.addColorStop(0.92, '#0369a1'); // Deep blue
        radGrad.addColorStop(1.0, '#041d2e');  // Dark limbal ring
        ctx.fillStyle = radGrad;
        ctx.fillRect(0, 0, 512, 512);

        // Radial stroma striations (200+ fine micro-filaments)
        ctx.lineWidth = 1.0;
        for (let a = 0; a < Math.PI * 2; a += 0.015) {
            ctx.beginPath();
            const rStart = 45 + Math.random() * 15;
            const rEnd = 245 - Math.random() * 10;
            ctx.moveTo(cx + Math.cos(a) * rStart, cy + Math.sin(a) * rStart);
            ctx.lineTo(cx + Math.cos(a) * rEnd, cy + Math.sin(a) * rEnd);

            const colorRnd = Math.random();
            if (colorRnd > 0.65) {
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.45)';
            } else if (colorRnd > 0.3) {
                ctx.strokeStyle = 'rgba(125, 211, 252, 0.5)';
            } else {
                ctx.strokeStyle = 'rgba(251, 191, 36, 0.35)';
            }
            ctx.stroke();
        }

        // Concentric contraction furrows
        [110, 160, 205].forEach(radius => {
            ctx.beginPath();
            ctx.arc(cx, cy, radius, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(15, 23, 42, 0.4)';
            ctx.lineWidth = 2.5;
            ctx.stroke();
        });

        // Golden collarette ring
        ctx.beginPath();
        ctx.arc(cx, cy, 90, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.5)';
        ctx.lineWidth = 3.5;
        ctx.stroke();

        const texture = new THREE.CanvasTexture(canvas);
        return texture;
    }

    // Helper: Generate procedural Retina fundus texture with warm orange-red base, optic disc & vascular tree
    function createRetinaTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 1024;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');

        // Rich, warm retinal fundus base gradient (warm orange-red to deep arterial red)
        const bg = ctx.createRadialGradient(512, 256, 30, 512, 256, 500);
        bg.addColorStop(0, '#ea580c');  // Warm orange-red central fundus
        bg.addColorStop(0.4, '#dc2626'); // Rich arterial red
        bg.addColorStop(0.75, '#b91c1c');// Deep retinal red
        bg.addColorStop(1.0, '#7f1d1d'); // Peripheral dark red
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, 1024, 512);

        // Optic Disc (bright yellow-golden oval at nasal pole)
        const discX = 360, discY = 256;
        const discGrad = ctx.createRadialGradient(discX, discY, 3, discX, discY, 32);
        discGrad.addColorStop(0, '#fef08a');
        discGrad.addColorStop(0.65, '#facc15');
        discGrad.addColorStop(1.0, '#ca8a04');
        ctx.fillStyle = discGrad;
        ctx.beginPath();
        ctx.arc(discX, discY, 30, 0, Math.PI * 2);
        ctx.fill();

        // Central physiologic cup inside optic disc
        ctx.fillStyle = '#fef9c3';
        ctx.beginPath();
        ctx.arc(discX, discY, 12, 0, Math.PI * 2);
        ctx.fill();

        // Macula Lutea & Fovea Centralis (darker avascular luteal zone)
        const macX = 660, macY = 256;
        const macGrad = ctx.createRadialGradient(macX, macY, 5, macX, macY, 45);
        macGrad.addColorStop(0, '#450a0a');
        macGrad.addColorStop(0.7, '#7f1d1d');
        macGrad.addColorStop(1.0, 'transparent');
        ctx.fillStyle = macGrad;
        ctx.beginPath();
        ctx.arc(macX, macY, 45, 0, Math.PI * 2);
        ctx.fill();

        // Foveal pit center
        ctx.fillStyle = '#260404';
        ctx.beginPath();
        ctx.arc(macX, macY, 7, 0, Math.PI * 2);
        ctx.fill();

        // Branching retinal arterial and venous arcades originating from the optic disc
        const arcades = [
            // Superior Temporal Arcade
            [[discX, discY], [410, 160], [530, 95], [670, 90], [800, 130], [920, 180]],
            // Inferior Temporal Arcade
            [[discX, discY], [410, 350], [530, 415], [670, 420], [800, 380], [920, 330]],
            // Superior Nasal Branch
            [[discX, discY], [270, 175], [170, 125], [70, 110]],
            // Inferior Nasal Branch
            [[discX, discY], [270, 335], [170, 385], [70, 400]]
        ];

        // Draw main vessels (arteriolar red & venous dark red)
        arcades.forEach((arc, idx) => {
            // Main trunk
            ctx.strokeStyle = idx % 2 === 0 ? 'rgba(153, 27, 27, 0.95)' : 'rgba(185, 28, 28, 0.9)';
            ctx.lineWidth = 4.0;
            ctx.beginPath();
            ctx.moveTo(arc[0][0], arc[0][1]);
            for (let k = 1; k < arc.length; k++) {
                ctx.lineTo(arc[k][0], arc[k][1]);
            }
            ctx.stroke();

            // Secondary branches
            ctx.lineWidth = 2.0;
            for (let k = 1; k < arc.length - 1; k++) {
                const pt = arc[k];
                ctx.beginPath();
                ctx.moveTo(pt[0], pt[1]);
                const sign = k % 2 === 0 ? 1 : -1;
                ctx.lineTo(pt[0] + 35 * sign, pt[1] + 40 * sign);
                ctx.stroke();
            }

            // Tertiary terminal micro-arterioles
            ctx.lineWidth = 1.0;
            for (let k = 1; k < arc.length; k++) {
                const pt = arc[k];
                ctx.beginPath();
                ctx.moveTo(pt[0], pt[1]);
                ctx.lineTo(pt[0] + (Math.random() - 0.5) * 30, pt[1] + (Math.random() - 0.5) * 30);
                ctx.stroke();
            }
        });

        const texture = new THREE.CanvasTexture(canvas);
        texture.wrapS = THREE.RepeatWrapping;
        return texture;
    }

    // Main 3D Anatomical Eye Controller
    function initEyeViewer() {
        const container = document.getElementById('eyeCanvasContainer');
        if (!container || typeof THREE === 'undefined') return;

        // Clean container
        container.innerHTML = '';

        const width = container.clientWidth || 540;
        const height = container.clientHeight || 420;

        // Scene
        const scene = new THREE.Scene();

        // Camera
        const camera = new THREE.PerspectiveCamera(36, width / height, 0.1, 1000);
        camera.position.set(0, 0.8, 7.4);

        // WebGL Renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.outputEncoding = THREE.sRGBEncoding;
        container.appendChild(renderer.domElement);

        // Balanced Professional Lighting (Prevents Bleached Washout)
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.45);
        scene.add(ambientLight);

        const keyLight = new THREE.DirectionalLight(0xfff8ee, 1.1);
        keyLight.position.set(4, 6, 6);
        scene.add(keyLight);

        const fillLight = new THREE.DirectionalLight(0x93c5fd, 0.4);
        fillLight.position.set(-5, -2, 4);
        scene.add(fillLight);

        const rimLight = new THREE.DirectionalLight(0x10b981, 0.5);
        rimLight.position.set(0, 5, -6);
        scene.add(rimLight);

        // Root Group
        const eyeGroup = new THREE.Group();
        scene.add(eyeGroup);

        // Textures
        const scleraTex = createScleraTexture();
        const irisTex = createIrisTexture();
        const retinaTex = createRetinaTexture();

        const layers = {};
        const layerMeshes = [];

        // -------------------------------------------------------------
        // 1. Sclera (Outer Fibrous Protective Shell)
        // -------------------------------------------------------------
        // Geometry rotated so anterior opening meets corneal limbus (+Z)
        const scleraGeo = new THREE.SphereGeometry(2.0, 48, 36, 0, Math.PI * 2, 0.45, Math.PI - 0.55);
        scleraGeo.rotateX(Math.PI / 2);
        const scleraMat = new THREE.MeshStandardMaterial({
            map: scleraTex,
            color: 0xedeae4,
            roughness: 0.42,
            metalness: 0.02,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 1.0
        });
        const scleraMesh = new THREE.Mesh(scleraGeo, scleraMat);
        scleraMesh.userData = {
            layerId: 'sclera',
            name: 'Sclera',
            assembledPos: new THREE.Vector3(0, 0, 0),
            explodedPos: new THREE.Vector3(0, 0, -3.4)
        };
        eyeGroup.add(scleraMesh);
        layers['sclera'] = scleraMesh;
        layerMeshes.push(scleraMesh);

        // -------------------------------------------------------------
        // 2. Choroid (Vascular Middle Tunic)
        // -------------------------------------------------------------
        const choroidGeo = new THREE.SphereGeometry(1.92, 44, 32, 0, Math.PI * 2, 0.5, Math.PI - 0.65);
        choroidGeo.rotateX(Math.PI / 2);
        const choroidMat = new THREE.MeshStandardMaterial({
            color: 0x3d140e,
            roughness: 0.65,
            metalness: 0.05,
            side: THREE.DoubleSide
        });
        const choroidMesh = new THREE.Mesh(choroidGeo, choroidMat);
        choroidMesh.userData = {
            layerId: 'choroid',
            name: 'Choroid',
            assembledPos: new THREE.Vector3(0, 0, 0),
            explodedPos: new THREE.Vector3(0, 0, -2.0)
        };
        eyeGroup.add(choroidMesh);
        layers['choroid'] = choroidMesh;
        layerMeshes.push(choroidMesh);

        // -------------------------------------------------------------
        // 3. Retina (Neurosensory Inner Tunic ★ DR Target)
        // -------------------------------------------------------------
        const retinaGeo = new THREE.SphereGeometry(1.85, 48, 36, 0, Math.PI * 2, 0.55, Math.PI - 0.7);
        retinaGeo.rotateX(Math.PI / 2);
        const retinaMat = new THREE.MeshStandardMaterial({
            map: retinaTex,
            color: 0xffffff,
            roughness: 0.48,
            metalness: 0.02,
            side: THREE.DoubleSide
        });
        const retinaMesh = new THREE.Mesh(retinaGeo, retinaMat);
        retinaMesh.userData = {
            layerId: 'retina',
            name: 'Retina',
            assembledPos: new THREE.Vector3(0, 0, 0),
            explodedPos: new THREE.Vector3(0, 0, -0.6)
        };
        eyeGroup.add(retinaMesh);
        layers['retina'] = retinaMesh;
        layerMeshes.push(retinaMesh);

        // -------------------------------------------------------------
        // 4. Crystalline Lens (Translucent Biconvex Body)
        // -------------------------------------------------------------
        const lensGeo = new THREE.SphereGeometry(0.85, 32, 24);
        lensGeo.scale(1.0, 1.0, 0.45);
        const lensMat = new THREE.MeshPhysicalMaterial({
            color: 0xbae6fd,
            transparent: true,
            opacity: 0.55,
            roughness: 0.1,
            metalness: 0.05,
            transmission: 0.8,
            ior: 1.41,
            clearcoat: 0.8,
            depthWrite: false,
            side: THREE.DoubleSide
        });
        const lensMesh = new THREE.Mesh(lensGeo, lensMat);
        lensMesh.position.set(0, 0, 0.75);
        lensMesh.userData = {
            layerId: 'lens',
            name: 'Lens',
            assembledPos: new THREE.Vector3(0, 0, 0.75),
            explodedPos: new THREE.Vector3(0, 0, 0.9)
        };
        eyeGroup.add(lensMesh);
        layers['lens'] = lensMesh;
        layerMeshes.push(lensMesh);

        // -------------------------------------------------------------
        // 5. Iris (Pigmented Circular Ring Diaphragm)
        // -------------------------------------------------------------
        const irisGeo = new THREE.RingGeometry(0.4, 1.32, 48);
        const irisMat = new THREE.MeshStandardMaterial({
            map: irisTex,
            roughness: 0.45,
            metalness: 0.05,
            side: THREE.DoubleSide
        });
        const irisMesh = new THREE.Mesh(irisGeo, irisMat);
        irisMesh.position.set(0, 0, 1.15);
        irisMesh.userData = {
            layerId: 'iris',
            name: 'Iris',
            assembledPos: new THREE.Vector3(0, 0, 1.15),
            explodedPos: new THREE.Vector3(0, 0, 2.1)
        };
        eyeGroup.add(irisMesh);
        layers['iris'] = irisMesh;
        layerMeshes.push(irisMesh);

        // -------------------------------------------------------------
        // 6. Pupil (Deep Black Optical Aperture Disc)
        // -------------------------------------------------------------
        const pupilGeo = new THREE.CircleGeometry(0.4, 36);
        const pupilMat = new THREE.MeshBasicMaterial({
            color: 0x020202,
            side: THREE.DoubleSide
        });
        const pupilMesh = new THREE.Mesh(pupilGeo, pupilMat);
        pupilMesh.position.set(0, 0, 1.14);
        pupilMesh.userData = {
            layerId: 'pupil',
            name: 'Pupil',
            assembledPos: new THREE.Vector3(0, 0, 1.14),
            explodedPos: new THREE.Vector3(0, 0, 2.09)
        };
        eyeGroup.add(pupilMesh);
        layers['pupil'] = pupilMesh;
        layerMeshes.push(pupilMesh);

        // -------------------------------------------------------------
        // 7. Cornea (Anterior Refractive Transparent Dome)
        // -------------------------------------------------------------
        const corneaGeo = new THREE.SphereGeometry(1.35, 36, 24, 0, Math.PI * 2, 0, 1.0);
        corneaGeo.rotateX(Math.PI / 2);
        const corneaMat = new THREE.MeshPhysicalMaterial({
            color: 0xe0f7fa,
            transparent: true,
            opacity: 0.18,
            roughness: 0.05,
            metalness: 0.0,
            transmission: 0.92,
            ior: 1.376,
            clearcoat: 1.0,
            clearcoatRoughness: 0.05,
            depthWrite: false,
            side: THREE.FrontSide
        });
        const corneaMesh = new THREE.Mesh(corneaGeo, corneaMat);
        corneaMesh.position.set(0, 0, 0.75);
        corneaMesh.userData = {
            layerId: 'cornea',
            name: 'Cornea',
            assembledPos: new THREE.Vector3(0, 0, 0.75),
            explodedPos: new THREE.Vector3(0, 0, 3.4)
        };
        eyeGroup.add(corneaMesh);
        layers['cornea'] = corneaMesh;
        layerMeshes.push(corneaMesh);

        // -------------------------------------------------------------
        // 8. Optic Nerve (Posterior Myelinated Cylinder Bundle)
        // -------------------------------------------------------------
        const opticGeo = new THREE.CylinderGeometry(0.36, 0.42, 1.8, 32);
        opticGeo.rotateX(Math.PI / 2);
        const opticMat = new THREE.MeshStandardMaterial({
            color: 0xf3ecd8,
            roughness: 0.55,
            metalness: 0.05
        });
        const opticMesh = new THREE.Mesh(opticGeo, opticMat);
        opticMesh.position.set(0, 0, -2.5);
        opticMesh.userData = {
            layerId: 'optic_nerve',
            name: 'Optic Nerve',
            assembledPos: new THREE.Vector3(0, 0, -2.5),
            explodedPos: new THREE.Vector3(0, 0, -4.8)
        };
        eyeGroup.add(opticMesh);
        layers['optic_nerve'] = opticMesh;
        layerMeshes.push(opticMesh);

        // Set natural three-quarter perspective angle on load
        eyeGroup.rotation.set(0.18, 0.55, 0);

        // State
        let isExploded = false;
        let selectedLayerId = 'retina';
        let isDragging = false;
        let prevMousePos = { x: 0, y: 0 };
        let autoRotate = true;

        // Raycasting
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        // UI Binding Elements
        const titleEl = document.getElementById('eyeStructureTitle');
        const catEl = document.getElementById('eyeStructureCat');
        const descEl = document.getElementById('eyeStructureDesc');
        const clinicalEl = document.getElementById('eyeStructureClinical');
        const explodeBtn = document.getElementById('btnExplodeEye');
        const resetBtn = document.getElementById('btnResetEye');
        const zoomInBtn = document.getElementById('btnZoomIn');
        const zoomOutBtn = document.getElementById('btnZoomOut');
        const pills = document.querySelectorAll('.eye-layer-pill');

        function updateUI(layerId) {
            const data = ANATOMY_DATA[layerId] || ANATOMY_DATA['retina'];
            if (titleEl) titleEl.textContent = data.name;
            if (catEl) catEl.textContent = data.category;
            if (descEl) descEl.textContent = data.description;
            if (clinicalEl) {
                clinicalEl.innerHTML = `<strong class="text-emerald-400 font-mono text-[11px] d-block mb-1">CLINICAL PERSPECTIVE:</strong> ${data.clinical}`;
            }

            pills.forEach(p => {
                if (p.getAttribute('data-layer') === layerId) {
                    p.classList.add('active');
                } else {
                    p.classList.remove('active');
                }
            });
        }

        function highlightLayer(layerId) {
            selectedLayerId = layerId;
            layerMeshes.forEach(mesh => {
                const isSelected = mesh.userData.layerId === layerId;
                if (isSelected) {
                    if (mesh.material.emissive) {
                        const cfg = LAYER_EMISSIVE_CONFIG[layerId] || { color: 0x10b981, intensity: 0.25 };
                        mesh.material.emissive.setHex(cfg.color);
                        mesh.material.emissiveIntensity = cfg.intensity;
                    }
                } else {
                    if (mesh.material.emissive) {
                        mesh.material.emissive.setHex(0x000000);
                        mesh.material.emissiveIntensity = 0.0;
                    }
                }
            });

            // In assembled mode, if internal layer is selected, make sclera semi-transparent so internal structures are visible!
            if (!isExploded && scleraMesh && scleraMesh.material) {
                if (layerId === 'retina' || layerId === 'choroid' || layerId === 'lens') {
                    scleraMesh.material.opacity = 0.28;
                } else {
                    scleraMesh.material.opacity = 1.0;
                }
            }

            updateUI(layerId);
        }

        // Initialize with Retina highlighted
        highlightLayer('retina');

        // Exploded view toggle
        if (explodeBtn) {
            explodeBtn.addEventListener('click', () => {
                isExploded = !isExploded;
                explodeBtn.innerHTML = isExploded ?
                    `<i class="fa-solid fa-compress me-1 text-emerald-400"></i> Assemble View` :
                    `<i class="fa-solid fa-layer-group me-1 text-emerald-400"></i> Explode Layers`;

                // When exploded, sclera stays fully opaque since layers are separated in space
                if (scleraMesh && scleraMesh.material) {
                    if (isExploded) {
                        scleraMesh.material.opacity = 0.95;
                    } else if (selectedLayerId === 'retina' || selectedLayerId === 'choroid' || selectedLayerId === 'lens') {
                        scleraMesh.material.opacity = 0.28;
                    } else {
                        scleraMesh.material.opacity = 1.0;
                    }
                }
            });
        }

        // Reset view
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                isExploded = false;
                if (explodeBtn) {
                    explodeBtn.innerHTML = `<i class="fa-solid fa-layer-group me-1 text-emerald-400"></i> Explode Layers`;
                }
                eyeGroup.rotation.set(0.18, 0.55, 0);
                camera.position.set(0, 0.8, 7.4);
                highlightLayer('retina');
            });
        }

        // Zoom controls
        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', () => {
                camera.position.z = Math.max(camera.position.z - 0.8, 4.0);
            });
        }
        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', () => {
                camera.position.z = Math.min(camera.position.z + 0.8, 12.0);
            });
        }

        // Layer selection pills
        pills.forEach(pill => {
            pill.addEventListener('click', function () {
                const target = this.getAttribute('data-layer');
                if (target === 'all') {
                    layerMeshes.forEach(m => {
                        if (m.material.emissive) m.material.emissive.setHex(0x000000);
                    });
                    if (scleraMesh && scleraMesh.material) {
                        scleraMesh.material.opacity = 1.0;
                    }
                    if (titleEl) titleEl.textContent = 'Whole Anatomical Eye';
                    if (catEl) catEl.textContent = 'Multi-Layered Optical System';
                    if (descEl) descEl.textContent = 'The human eye is an advanced optical organ consisting of three tunics: fibrous outer sclera/cornea, vascular uveal tract, and inner neurosensory retina.';
                    pills.forEach(p => p.classList.remove('active'));
                    this.classList.add('active');
                } else if (ANATOMY_DATA[target]) {
                    highlightLayer(target);
                }
            });
        });

        // Mouse drag rotation on canvas
        const dom = renderer.domElement;
        dom.style.cursor = 'grab';

        dom.addEventListener('mousedown', (e) => {
            isDragging = true;
            autoRotate = false;
            dom.style.cursor = 'grabbing';
            prevMousePos = { x: e.clientX, y: e.clientY };
        });

        window.addEventListener('mouseup', () => {
            isDragging = false;
            dom.style.cursor = 'grab';
        });

        window.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const deltaX = e.clientX - prevMousePos.x;
            const deltaY = e.clientY - prevMousePos.y;
            eyeGroup.rotation.y += deltaX * 0.008;
            eyeGroup.rotation.x += deltaY * 0.008;
            prevMousePos = { x: e.clientX, y: e.clientY };
        });

        // Touch drag for mobile
        dom.addEventListener('touchstart', (e) => {
            if (e.touches.length === 1) {
                isDragging = true;
                autoRotate = false;
                prevMousePos = { x: e.touches[0].clientX, y: e.touches[0].clientY };
            }
        }, { passive: true });

        dom.addEventListener('touchmove', (e) => {
            if (isDragging && e.touches.length === 1) {
                const deltaX = e.touches[0].clientX - prevMousePos.x;
                const deltaY = e.touches[0].clientY - prevMousePos.y;
                eyeGroup.rotation.y += deltaX * 0.01;
                eyeGroup.rotation.x += deltaY * 0.01;
                prevMousePos = { x: e.touches[0].clientX, y: e.touches[0].clientY };
            }
        }, { passive: true });

        dom.addEventListener('touchend', () => { isDragging = false; });

        // Wheel zoom
        dom.addEventListener('wheel', (e) => {
            e.preventDefault();
            camera.position.z += e.deltaY * 0.005;
            camera.position.z = Math.min(Math.max(camera.position.z, 4.0), 12.0);
        }, { passive: false });

        // Click raycasting to pick layers
        dom.addEventListener('click', (e) => {
            const rect = dom.getBoundingClientRect();
            mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(layerMeshes, true);

            if (intersects.length > 0) {
                let hitMesh = intersects[0].object;
                // Allow picking underlying layer if transparent cornea is clicked in assembled view
                if (hitMesh.userData.layerId === 'cornea' && intersects.length > 1 && !isExploded) {
                    hitMesh = intersects[1].object;
                }
                if (hitMesh.userData && hitMesh.userData.layerId) {
                    highlightLayer(hitMesh.userData.layerId);
                }
            }
        });

        // Resize handling
        window.addEventListener('resize', () => {
            if (!container) return;
            const newW = container.clientWidth;
            const newH = container.clientHeight || 420;
            camera.aspect = newW / newH;
            camera.updateProjectionMatrix();
            renderer.setSize(newW, newH);
        });

        // Animation Loop
        function animate() {
            requestAnimationFrame(animate);

            // Smooth interpolation for exploded layers
            layerMeshes.forEach(mesh => {
                const target = isExploded ? mesh.userData.explodedPos : mesh.userData.assembledPos;
                if (target) {
                    mesh.position.lerp(target, 0.08);
                }
            });

            // Slow gentle auto-rotation when user is not dragging
            if (autoRotate && !isDragging) {
                eyeGroup.rotation.y += 0.0018;
            }

            renderer.render(scene, camera);
        }

        animate();
    }

    // Auto-mount when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initEyeViewer);
    } else {
        initEyeViewer();
    }
})();
