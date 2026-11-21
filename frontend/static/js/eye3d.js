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
            description: 'The opaque, protective white outer layer composed of dense collagenous fibers. It maintains intraocular pressure, ocular volume, and structural shape, anchoring the extraocular muscles.',
            clinical: 'Maintains ocular structural integrity and resists tensile intraocular stresses, protecting internal delicate sensory and vascular tunics.'
        },
        'optic_nerve': {
            name: 'Optic Nerve (CN II)',
            category: 'Central Visual Pathway',
            description: 'A bundle of over one million myelinated retinal ganglion cell axons exiting through the lamina cribrosa, transmitting visual impulses to the lateral geniculate nucleus and visual cortex.',
            clinical: 'Neovascularization at the Optic Disc (NVD) represents one of the highest-risk indicators of proliferative diabetic retinopathy, requiring urgent retinal laser photocoagulation or anti-VEGF therapy.'
        }
    };

    // Helper: Generate procedural Sclera texture with fine micro-vessels
    function createScleraTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 1024;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');

        // Pearly white base
        const grad = ctx.createLinearGradient(0, 0, 1024, 512);
        grad.addColorStop(0, '#f8f8fb');
        grad.addColorStop(0.5, '#eaeef2');
        grad.addColorStop(1, '#f1f4f8');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 1024, 512);

        // Micro-vasculature (fine red ciliary blood vessel filaments)
        ctx.strokeStyle = 'rgba(215, 45, 45, 0.45)';
        ctx.lineWidth = 1.2;
        for (let i = 0; i < 40; i++) {
            ctx.beginPath();
            let x = Math.random() * 1024;
            let y = Math.random() * 512;
            ctx.moveTo(x, y);
            for (let j = 0; j < 5; j++) {
                x += (Math.random() - 0.5) * 60;
                y += (Math.random() - 0.5) * 40;
                ctx.lineTo(x, y);
            }
            ctx.stroke();
        }

        const texture = new THREE.CanvasTexture(canvas);
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.ClampToEdgeWrapping;
        return texture;
    }

    // Helper: Generate procedural Iris texture with radial stroma fibers
    function createIrisTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');
        const cx = 256, cy = 256;

        // Base gradient (Cyan / Emerald hazel clinical tone)
        const radGrad = ctx.createRadialGradient(cx, cy, 30, cx, cy, 250);
        radGrad.addColorStop(0, '#021820');
        radGrad.addColorStop(0.2, '#0f5257');
        radGrad.addColorStop(0.5, '#10b981');
        radGrad.addColorStop(0.75, '#0b7285');
        radGrad.addColorStop(0.95, '#042f2e');
        radGrad.addColorStop(1.0, '#021214');
        ctx.fillStyle = radGrad;
        ctx.fillRect(0, 0, 512, 512);

        // Radial stroma striations
        ctx.lineWidth = 1.0;
        for (let a = 0; a < Math.PI * 2; a += 0.02) {
            ctx.beginPath();
            const rStart = 45 + Math.random() * 20;
            const rEnd = 245 - Math.random() * 10;
            ctx.moveTo(cx + Math.cos(a) * rStart, cy + Math.sin(a) * rStart);
            ctx.lineTo(cx + Math.cos(a) * rEnd, cy + Math.sin(a) * rEnd);
            ctx.strokeStyle = Math.random() > 0.5 ? 'rgba(255, 255, 255, 0.45)' : 'rgba(52, 211, 153, 0.5)';
            ctx.stroke();
        }

        // Sphincter ring
        ctx.beginPath();
        ctx.arc(cx, cy, 85, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(251, 191, 36, 0.35)';
        ctx.lineWidth = 4;
        ctx.stroke();

        const texture = new THREE.CanvasTexture(canvas);
        return texture;
    }

    // Helper: Generate procedural Retina fundus texture with branching vascular arcades
    function createRetinaTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 1024;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');

        // Warm reddish-orange retinal base
        const bg = ctx.createRadialGradient(512, 256, 40, 512, 256, 480);
        bg.addColorStop(0, '#c2410c');
        bg.addColorStop(0.6, '#991b1b');
        bg.addColorStop(1, '#450a0a');
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, 1024, 512);

        // Optic Disc (yellowish-bright circle at nasal pole)
        const discX = 360, discY = 256;
        const discGrad = ctx.createRadialGradient(discX, discY, 5, discX, discY, 35);
        discGrad.addColorStop(0, '#fef08a');
        discGrad.addColorStop(0.7, '#facc15');
        discGrad.addColorStop(1, '#b45309');
        ctx.fillStyle = discGrad;
        ctx.beginPath();
        ctx.arc(discX, discY, 32, 0, Math.PI * 2);
        ctx.fill();

        // Macula / Fovea (dark reddish zone)
        const macX = 640, macY = 256;
        ctx.fillStyle = 'rgba(69, 10, 10, 0.7)';
        ctx.beginPath();
        ctx.arc(macX, macY, 40, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#1c0404';
        ctx.beginPath();
        ctx.arc(macX, macY, 8, 0, Math.PI * 2);
        ctx.fill();

        // Retinal vascular arcades branching from optic disc
        ctx.strokeStyle = 'rgba(127, 29, 29, 0.9)';
        const branches = [
            [[discX, discY], [420, 160], [540, 100], [700, 110], [850, 160]],
            [[discX, discY], [420, 350], [540, 410], [700, 400], [850, 350]],
            [[discX, discY], [260, 180], [160, 140]],
            [[discX, discY], [260, 330], [160, 370]]
        ];

        branches.forEach(branch => {
            ctx.lineWidth = 3.5;
            ctx.beginPath();
            ctx.moveTo(branch[0][0], branch[0][1]);
            for (let k = 1; k < branch.length; k++) {
                ctx.lineTo(branch[k][0], branch[k][1]);
            }
            ctx.stroke();

            // Smaller arteriolar twigs
            ctx.lineWidth = 1.5;
            for (let k = 1; k < branch.length; k++) {
                const bx = branch[k][0], by = branch[k][1];
                ctx.beginPath();
                ctx.moveTo(bx, by);
                ctx.lineTo(bx + (Math.random() - 0.5) * 50, by + (Math.random() - 0.5) * 50);
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
        const camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 1000);
        camera.position.set(0, 0.8, 7.2);

        // WebGL Renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.outputEncoding = THREE.sRGBEncoding;
        container.appendChild(renderer.domElement);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
        scene.add(ambientLight);

        const keyLight = new THREE.DirectionalLight(0xffffff, 1.6);
        keyLight.position.set(5, 8, 8);
        scene.add(keyLight);

        const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.6);
        fillLight.position.set(-6, -3, 4);
        scene.add(fillLight);

        const rimLight = new THREE.DirectionalLight(0x10b981, 1.2);
        rimLight.position.set(0, -6, -8);
        scene.add(rimLight);

        // Eye Group
        const eyeGroup = new THREE.Group();
        scene.add(eyeGroup);

        // Materials & Textures
        const scleraTex = createScleraTexture();
        const irisTex = createIrisTexture();
        const retinaTex = createRetinaTexture();

        const layers = {};
        const layerMeshes = [];

        // 1. Sclera (Outer White Sphere Shell - Cutaway to allow viewing inside)
        const scleraGeo = new THREE.SphereGeometry(2.0, 48, 48, 0, Math.PI * 2, 0.42, Math.PI - 0.55);
        const scleraMat = new THREE.MeshStandardMaterial({
            map: scleraTex,
            roughness: 0.35,
            metalness: 0.05,
            side: THREE.DoubleSide
        });
        const scleraMesh = new THREE.Mesh(scleraGeo, scleraMat);
        scleraMesh.userData = {
            layerId: 'sclera',
            name: 'Sclera',
            assembledPos: new THREE.Vector3(0, 0, 0),
            explodedPos: new THREE.Vector3(0, 0, -1.8)
        };
        eyeGroup.add(scleraMesh);
        layers['sclera'] = scleraMesh;
        layerMeshes.push(scleraMesh);

        // 2. Choroid (Vascular Layer Shell)
        const choroidGeo = new THREE.SphereGeometry(1.92, 40, 40, 0, Math.PI * 2, 0.5, Math.PI - 0.7);
        const choroidMat = new THREE.MeshStandardMaterial({
            color: 0x3b120c,
            roughness: 0.6,
            side: THREE.DoubleSide
        });
        const choroidMesh = new THREE.Mesh(choroidGeo, choroidMat);
        choroidMesh.userData = {
            layerId: 'choroid',
            name: 'Choroid',
            assembledPos: new THREE.Vector3(0, 0, 0),
            explodedPos: new THREE.Vector3(0, 0, -1.1)
        };
        eyeGroup.add(choroidMesh);
        layers['choroid'] = choroidMesh;
        layerMeshes.push(choroidMesh);

        // 3. Retina (Sensory Inner Hemisphere)
        const retinaGeo = new THREE.SphereGeometry(1.85, 48, 48, 0, Math.PI * 2, 0.6, Math.PI - 0.85);
        const retinaMat = new THREE.MeshStandardMaterial({
            map: retinaTex,
            roughness: 0.45,
            side: THREE.DoubleSide
        });
        const retinaMesh = new THREE.Mesh(retinaGeo, retinaMat);
        retinaMesh.userData = {
            layerId: 'retina',
            name: 'Retina',
            assembledPos: new THREE.Vector3(0, 0, 0),
            explodedPos: new THREE.Vector3(0, 0, -0.4)
        };
        eyeGroup.add(retinaMesh);
        layers['retina'] = retinaMesh;
        layerMeshes.push(retinaMesh);

        // 4. Crystalline Lens (Biconvex Transparent Crystalline Body)
        const lensGeo = new THREE.SphereGeometry(0.85, 32, 24);
        lensGeo.scale(1.0, 1.0, 0.45);
        const lensMat = new THREE.MeshPhysicalMaterial({
            color: 0xe2f3f5,
            transparent: true,
            opacity: 0.65,
            roughness: 0.1,
            metalness: 0.1,
            transmission: 0.8,
            side: THREE.DoubleSide
        });
        const lensMesh = new THREE.Mesh(lensGeo, lensMat);
        lensMesh.position.set(0, 0, 1.1);
        lensMesh.userData = {
            layerId: 'lens',
            name: 'Lens',
            assembledPos: new THREE.Vector3(0, 0, 1.1),
            explodedPos: new THREE.Vector3(0, 0, 0.7)
        };
        eyeGroup.add(lensMesh);
        layers['lens'] = lensMesh;
        layerMeshes.push(lensMesh);

        // 5. Iris (Pigmented Circular Ring)
        const irisGeo = new THREE.RingGeometry(0.38, 1.25, 48);
        const irisMat = new THREE.MeshStandardMaterial({
            map: irisTex,
            roughness: 0.5,
            side: THREE.DoubleSide
        });
        const irisMesh = new THREE.Mesh(irisGeo, irisMat);
        irisMesh.position.set(0, 0, 1.55);
        irisMesh.userData = {
            layerId: 'iris',
            name: 'Iris',
            assembledPos: new THREE.Vector3(0, 0, 1.55),
            explodedPos: new THREE.Vector3(0, 0, 1.6)
        };
        eyeGroup.add(irisMesh);
        layers['iris'] = irisMesh;
        layerMeshes.push(irisMesh);

        // 6. Pupil (Deep Black Absorbing Aperture Disc)
        const pupilGeo = new THREE.CircleGeometry(0.38, 32);
        const pupilMat = new THREE.MeshBasicMaterial({
            color: 0x050505,
            side: THREE.DoubleSide
        });
        const pupilMesh = new THREE.Mesh(pupilGeo, pupilMat);
        pupilMesh.position.set(0, 0, 1.54);
        pupilMesh.userData = {
            layerId: 'pupil',
            name: 'Pupil',
            assembledPos: new THREE.Vector3(0, 0, 1.54),
            explodedPos: new THREE.Vector3(0, 0, 1.59)
        };
        eyeGroup.add(pupilMesh);
        layers['pupil'] = pupilMesh;
        layerMeshes.push(pupilMesh);

        // 7. Cornea (Anterior Protruding Transparent Glass Dome)
        const corneaGeo = new THREE.SphereGeometry(1.35, 36, 36, 0, Math.PI * 2, 0, 0.95);
        const corneaMat = new THREE.MeshPhysicalMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.38,
            roughness: 0.05,
            metalness: 0.1,
            transmission: 0.9,
            reflectivity: 0.9,
            side: THREE.DoubleSide
        });
        const corneaMesh = new THREE.Mesh(corneaGeo, corneaMat);
        corneaMesh.position.set(0, 0, 1.15);
        corneaMesh.userData = {
            layerId: 'cornea',
            name: 'Cornea',
            assembledPos: new THREE.Vector3(0, 0, 1.15),
            explodedPos: new THREE.Vector3(0, 0, 2.6)
        };
        eyeGroup.add(corneaMesh);
        layers['cornea'] = corneaMesh;
        layerMeshes.push(corneaMesh);

        // 8. Optic Nerve (Posterior Exiting Cylinder Bundle)
        const opticGeo = new THREE.CylinderGeometry(0.38, 0.44, 2.0, 32);
        opticGeo.rotateX(Math.PI / 2);
        const opticMat = new THREE.MeshStandardMaterial({
            color: 0xeeebe5,
            roughness: 0.5,
            metalness: 0.05
        });
        const opticMesh = new THREE.Mesh(opticGeo, opticMat);
        opticMesh.position.set(-0.25, 0, -2.4);
        opticMesh.userData = {
            layerId: 'optic_nerve',
            name: 'Optic Nerve',
            assembledPos: new THREE.Vector3(-0.25, 0, -2.4),
            explodedPos: new THREE.Vector3(-0.25, 0, -3.4)
        };
        eyeGroup.add(opticMesh);
        layers['optic_nerve'] = opticMesh;
        layerMeshes.push(opticMesh);

        // Set initial gentle angled perspective so both anterior (cornea/iris) and interior/posterior are visible
        eyeGroup.rotation.y = 0.55;
        eyeGroup.rotation.x = 0.15;

        // Exploded View State
        let isExploded = false;
        let selectedLayerId = 'retina'; // Default active layer highlighting Diabetic Retinopathy

        // Interaction state
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
                if (mesh.userData.layerId === layerId) {
                    if (mesh.material.emissive) {
                        mesh.material.emissive.setHex(0x10b981);
                        mesh.material.emissiveIntensity = 0.45;
                    }
                } else {
                    if (mesh.material.emissive) {
                        mesh.material.emissive.setHex(0x000000);
                        mesh.material.emissiveIntensity = 0.0;
                    }
                }
            });
            updateUI(layerId);
        }

        // Initialize with Retina highlighted
        highlightLayer('retina');

        // Exploded view toggle
        if (explodeBtn) {
            explodeBtn.addEventListener('click', () => {
                isExploded = !isExploded;
                explodeBtn.innerHTML = isExploded ?
                    `<i class="fa-solid fa-compress me-1 text-emerald-400"></i> Assemble` :
                    `<i class="fa-solid fa-layer-group me-1 text-emerald-400"></i> Explode Layers`;
            });
        }

        // Reset view
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                isExploded = false;
                if (explodeBtn) {
                    explodeBtn.innerHTML = `<i class="fa-solid fa-layer-group me-1 text-emerald-400"></i> Explode Layers`;
                }
                eyeGroup.rotation.set(0.15, 0.55, 0);
                camera.position.set(0, 0.8, 7.2);
                highlightLayer('retina');
            });
        }

        // Zoom controls
        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', () => {
                camera.position.z = Math.max(camera.position.z - 0.8, 3.8);
            });
        }
        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', () => {
                camera.position.z = Math.min(camera.position.z + 0.8, 11.0);
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
            camera.position.z = Math.min(Math.max(camera.position.z, 3.8), 11.0);
        }, { passive: false });

        // Click raycasting to pick layers
        dom.addEventListener('click', (e) => {
            const rect = dom.getBoundingClientRect();
            mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(layerMeshes, true);

            if (intersects.length > 0) {
                const hit = intersects[0].object;
                if (hit.userData && hit.userData.layerId) {
                    highlightLayer(hit.userData.layerId);
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
                    mesh.position.lerp(target, 0.075);
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

