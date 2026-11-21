/**
 * AXIOM HEALTH &bull; Autonomous Medical AI Platform
 * Interactive Engine: Cursor Aura, Live Terminal, Dynamic Range Sliders, Presets & Inference
 */

document.addEventListener('DOMContentLoaded', function () {
    
    // -------------------------------------------------------------
    // 1. Cursor Aura Flashlight (Axiom CursorAura effect)
    // -------------------------------------------------------------
    const aura = document.getElementById('cursorAura');
    if (aura) {
        let currentX = window.innerWidth / 2;
        let currentY = window.innerHeight / 2;
        let targetX = currentX;
        let targetY = currentY;

        window.addEventListener('mousemove', (e) => {
            targetX = e.clientX;
            targetY = e.clientY;
        }, { passive: true });

        function renderAura() {
            currentX += (targetX - currentX) * 0.08;
            currentY += (targetY - currentY) * 0.08;
            
            aura.style.background = `radial-gradient(600px circle at ${currentX}px ${currentY}px, rgba(255, 255, 255, 0.04) 0%, rgba(16, 185, 129, 0.015) 30%, transparent 65%)`;
            requestAnimationFrame(renderAura);
        }
        requestAnimationFrame(renderAura);
    }

    // -------------------------------------------------------------
    // 2. Mobile Navigation Toggle
    // -------------------------------------------------------------
    const mobileToggle = document.getElementById('mobileNavToggle');
    const mobileDrawer = document.getElementById('mobileNavDrawer');
    if (mobileToggle && mobileDrawer) {
        mobileToggle.addEventListener('click', () => {
            mobileDrawer.classList.toggle('d-none');
        });
    }

    // -------------------------------------------------------------
    // 3. Live Telemetry Terminal Console Log Streamer
    // -------------------------------------------------------------
    const terminalLogs = document.getElementById('terminalLogs');
    if (terminalLogs) {
        const streamLogs = [
            "[CONSENSUS] PIMA holdout verification: 74.68% accuracy confirmed.",
            "[CALIBRATING] Random Forest decision tree split on Fasting Glucose (cutoff: 127 mg/dL).",
            "[INFERENCE] Z-score transform applied via StandardScaler (mean unit variance).",
            "[TELEMETRY] Secondary risk weight evaluated on BMI distribution (Gini 0.228).",
            "[HEALTH] Diagnostic node listening on REST endpoint /api/predict_diabetes.",
            "[AUDIT] SHA-256 patient case hash recorded in persistent SQLite registry.",
            "[MONITOR] MobileNetV2 retina vision tape standby (77.82% test accuracy)."
        ];
        
        let logIdx = 0;
        setInterval(() => {
            const p = document.createElement('div');
            p.className = 'terminal-line mb-1';
            const time = new Date().toLocaleTimeString('en-US', { hour12: false });
            p.innerHTML = `<span class="text-zinc-600 font-mono">[${time}]</span> <span class="text-emerald-400 font-mono">&gt;</span> <span class="text-zinc-300 font-mono">${streamLogs[logIdx % streamLogs.length]}</span>`;
            terminalLogs.appendChild(p);
            terminalLogs.scrollTop = terminalLogs.scrollHeight;
            logIdx++;
            
            if (terminalLogs.children.length > 25) {
                terminalLogs.removeChild(terminalLogs.children[0]);
            }
        }, 3000);
    }

    // -------------------------------------------------------------
    // 4. Biometric Sliders & Number Input Bidirectional Sync
    // -------------------------------------------------------------
    const featureKeys = [
        'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
        'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
    ];

    function updateSliderFill(rangeEl) {
        if (!rangeEl) return;
        const min = parseFloat(rangeEl.min) || 0;
        const max = parseFloat(rangeEl.max) || 100;
        const val = parseFloat(rangeEl.value) || 0;
        const percent = Math.min(Math.max(((val - min) / (max - min)) * 100, 0), 100);
        rangeEl.style.background = `linear-gradient(to right, #10B981 ${percent}%, #222222 ${percent}%)`;
    }

    featureKeys.forEach(key => {
        const rangeEl = document.getElementById(`range_${key}`);
        const inputEl = document.getElementById(`input_${key}`);

        if (rangeEl && inputEl) {
            updateSliderFill(rangeEl);

            rangeEl.addEventListener('input', function () {
                inputEl.value = this.value;
                updateSliderFill(this);
                updateLiveRiskPreview();
            });

            inputEl.addEventListener('input', function () {
                rangeEl.value = this.value;
                updateSliderFill(rangeEl);
                updateLiveRiskPreview();
            });
        }
    });

    // -------------------------------------------------------------
    // 5. Clinical Preset Profiles Loader
    // -------------------------------------------------------------
    const presetProfiles = {
        'optimal': {
            'Pregnancies': 0,
            'Glucose': 85,
            'BloodPressure': 68,
            'SkinThickness': 20,
            'Insulin': 75,
            'BMI': 21.8,
            'DiabetesPedigreeFunction': 0.18,
            'Age': 24
        },
        'borderline': {
            'Pregnancies': 2,
            'Glucose': 118,
            'BloodPressure': 76,
            'SkinThickness': 28,
            'Insulin': 140,
            'BMI': 28.4,
            'DiabetesPedigreeFunction': 0.42,
            'Age': 41
        },
        'highrisk': {
            'Pregnancies': 5,
            'Glucose': 172,
            'BloodPressure': 88,
            'SkinThickness': 35,
            'Insulin': 240,
            'BMI': 38.6,
            'DiabetesPedigreeFunction': 0.88,
            'Age': 54
        }
    };

    const presetButtons = document.querySelectorAll('.preset-pill');
    presetButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            presetButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const presetKey = this.getAttribute('data-preset');
            const data = presetProfiles[presetKey];
            if (data) {
                featureKeys.forEach(key => {
                    const rangeEl = document.getElementById(`range_${key}`);
                    const inputEl = document.getElementById(`input_${key}`);
                    if (rangeEl && inputEl) {
                        rangeEl.value = data[key];
                        inputEl.value = data[key];
                        updateSliderFill(rangeEl);
                    }
                });
                updateLiveRiskPreview();
            }
        });
    });

    function updateLiveRiskPreview() {
        const glucoseInput = document.getElementById('input_Glucose');
        const bmiInput = document.getElementById('input_BMI');
        const ageInput = document.getElementById('input_Age');
        const liveRiskMeter = document.getElementById('liveRiskMeter');
        const liveRiskLabel = document.getElementById('liveRiskLabel');

        if (glucoseInput && bmiInput && liveRiskMeter && liveRiskLabel) {
            const g = parseFloat(glucoseInput.value) || 100;
            const b = parseFloat(bmiInput.value) || 25;
            const a = parseFloat(ageInput ? ageInput.value : 30) || 30;

            // Fast empirical heuristic for real-time slider preview
            let score = ((g - 70) / 130) * 0.55 + ((b - 18) / 35) * 0.30 + ((a - 20) / 60) * 0.15;
            let percent = Math.min(Math.max(Math.round(score * 100), 4), 96);

            liveRiskMeter.style.width = percent + '%';
            if (percent < 35) {
                liveRiskMeter.className = 'progress-bar bg-emerald-500';
                liveRiskLabel.textContent = `Estimated ${percent}% (Low Risk)`;
                liveRiskLabel.className = 'text-emerald-400 font-mono text-xs';
            } else if (percent < 60) {
                liveRiskMeter.className = 'progress-bar bg-amber-500';
                liveRiskLabel.textContent = `Estimated ${percent}% (Moderate Risk)`;
                liveRiskLabel.className = 'text-amber-400 font-mono text-xs';
            } else {
                liveRiskMeter.className = 'progress-bar bg-rose-500';
                liveRiskLabel.textContent = `Estimated ${percent}% (High Diabetic Risk)`;
                liveRiskLabel.className = 'text-rose-400 font-mono text-xs';
            }
        }
    }

    // Run preview once on page load if inputs exist
    if (document.getElementById('input_Glucose')) {
        updateLiveRiskPreview();
    }

    // -------------------------------------------------------------
    // 6. Prediction Form AJAX Submission & Inline Result Rendering
    // -------------------------------------------------------------
    const diabetesForm = document.getElementById('diabetesPredictionForm');
    const predictBtn = document.getElementById('predictSubmitBtn');
    const loadingState = document.getElementById('predictLoadingState');
    const resultCard = document.getElementById('predictionResultCard');
    const predictAgainBtn = document.getElementById('predictAgainBtn');

    if (predictAgainBtn) {
        predictAgainBtn.addEventListener('click', function () {
            if (resultCard) resultCard.classList.add('d-none');
            if (diabetesForm) {
                diabetesForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }

    if (diabetesForm) {
        diabetesForm.addEventListener('submit', function (e) {
            e.preventDefault();

            if (predictBtn) {
                predictBtn.disabled = true;
                predictBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span> Evaluating Risk...`;
            }
            if (loadingState) {
                loadingState.classList.remove('d-none');
            }
            if (resultCard) {
                resultCard.classList.add('d-none');
            }

            const allFeatures = [
                'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
                'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
            ];

            const payload = {};
            allFeatures.forEach(k => {
                const el = document.getElementById(`input_${k}`);
                if (el) {
                    payload[k] = parseFloat(el.value);
                } else if (k === 'Glucose') {
                    payload[k] = 100.0;
                } else if (k === 'SkinThickness') {
                    payload[k] = 21.0;
                } else if (k === 'Insulin') {
                    payload[k] = 79.0;
                } else {
                    payload[k] = 0;
                }
            });

            const patientIdEl = document.getElementById('patientIdInput');
            const patientNameEl = document.getElementById('patientNameInput');
            const notesEl = document.getElementById('notesInput');

            payload['patient_id'] = patientIdEl && patientIdEl.value.trim() ? patientIdEl.value.trim() : `AX-${Math.floor(100000 + Math.random() * 900000)}`;
            payload['patient_name'] = patientNameEl && patientNameEl.value.trim() ? patientNameEl.value.trim() : "Anonymous Patient";
            payload['notes'] = notesEl ? notesEl.value.trim() : "";

            fetch('/api/predict_diabetes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (loadingState) loadingState.classList.add('d-none');
                if (predictBtn) {
                    predictBtn.disabled = false;
                    predictBtn.innerHTML = `<i class="fa-solid fa-bolt me-2"></i> Predict Diabetes Risk`;
                }

                if (data.success && data.result) {
                    const res = data.result;
                    const clsEl = document.getElementById('resultClassification');
                    const badgeEl = document.getElementById('resultRiskBadge');
                    const probEl = document.getElementById('resultProbability');
                    const tagEl = document.getElementById('resultClinicalTag');
                    const expEl = document.getElementById('resultExplanation');
                    const pdfBtn = document.getElementById('downloadPdfBtn');
                    const dossierBtn = document.getElementById('viewDossierBtn');

                    if (clsEl) clsEl.textContent = res.prediction_label;
                    if (probEl) {
                        probEl.textContent = `${res.probability_diabetic}%`;
                        if (res.probability_diabetic >= 60) {
                            probEl.className = 'font-display fw-bold fs-4 text-rose-400';
                        } else if (res.probability_diabetic >= 35) {
                            probEl.className = 'font-display fw-bold fs-4 text-amber-400';
                        } else {
                            probEl.className = 'font-display fw-bold fs-4 text-emerald-400';
                        }
                    }

                    if (badgeEl) {
                        badgeEl.textContent = res.risk_level;
                        if (res.risk_badge === 'rose') {
                            badgeEl.className = 'badge px-3 py-1 font-mono text-xs rounded-pill risk-badge-rose';
                        } else if (res.risk_badge === 'amber') {
                            badgeEl.className = 'badge px-3 py-1 font-mono text-xs rounded-pill risk-badge-amber';
                        } else {
                            badgeEl.className = 'badge px-3 py-1 font-mono text-xs rounded-pill risk-badge-emerald';
                        }
                    }

                    if (tagEl) tagEl.textContent = res.clinical_tag;
                    if (expEl) {
                        if (res.recommendations && res.recommendations.length > 0) {
                            expEl.textContent = res.recommendations[0];
                        } else {
                            expEl.textContent = `Random Forest ensemble evaluated probability: ${res.probability_diabetic}% (${res.risk_level}).`;
                        }
                    }

                    if (pdfBtn) pdfBtn.href = `/api/download_pdf/${data.record_id}`;
                    if (dossierBtn) dossierBtn.href = data.redirect_url;

                    if (resultCard) {
                        resultCard.classList.remove('d-none');
                        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                } else {
                    alert("Prediction Error: " + (data.error || "Unknown error"));
                }
            })
            .catch(err => {
                if (loadingState) loadingState.classList.add('d-none');
                if (predictBtn) {
                    predictBtn.disabled = false;
                    predictBtn.innerHTML = `<i class="fa-solid fa-bolt me-2"></i> Predict Diabetes Risk`;
                }
                alert("Network communication error: " + err.message);
            });
        });
    }

});
