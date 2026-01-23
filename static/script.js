$(document).ready(function () {

    // =====================
    // UI Elements
    // =====================
    const themeSwitch = $('#light-dark-mode-switch');
    const body = $('body');
    const chatWindow = $('#chat-window');
    const loadingUser = $('#loading-dots-user');
    const loadingAI = $('#loading-dots-ai');
    const recordBtn = $('#record-button');
    const messageList = $('#message-list');
    const voiceOptions = $('#voice-options');
    const instructionText = $('.instruction-text');

    // =====================
    // Session Management
    // =====================
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId) {
        sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);
        sessionStorage.setItem('sessionId', sessionId);
    }
    console.log("Current Session ID:", sessionId);

    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let recordingStartTime = 0;
    let recordingDuration = 0;

    // =====================
    // Theme Logic
    // =====================
    function applyTheme(isDark) {
        if (isDark) {
            body.addClass('dark-mode');
            chatWindow.addClass('dark');

            // Ensure loading dots match dark mode
            $('.dot').addClass('dark-dot');

            themeSwitch.prop('checked', true);
        } else {
            body.removeClass('dark-mode');
            chatWindow.removeClass('dark');

            $('.dot').removeClass('dark-dot');

            themeSwitch.prop('checked', false);
        }
    }

    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme === 'dark');

    themeSwitch.on('change', function () {
        const isDark = $(this).is(':checked');
        applyTheme(isDark);
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    // =====================
    // UI Helpers
    // =====================
    function expandChat() {
        $('.main-viewport').addClass('chat-active');
        chatWindow.addClass('active');
    }

    function showLoading(side) {
        // Clear all
        loadingUser.removeClass('active');
        loadingAI.removeClass('active');

        if (side === 'user') loadingUser.addClass('active');
        if (side === 'ai') loadingAI.addClass('active');
    }

    function hideLoading() {
        loadingUser.removeClass('active');
        loadingAI.removeClass('active');
    }

    function appendMessage(role, text, audioBase64 = null) {
        expandChat();

        const isUser = role === 'user';

        // Message row
        const msgDiv = $('<div>')
            .addClass(`message-line ${isUser ? 'my-text' : ''}`);

        // Message bubble
        const boxDiv = $('<div>')
            .addClass(`message-box ${isUser ? 'my-text' : ''}`);

        // Dark mode bubble styling
        if (body.hasClass('dark-mode')) {
            boxDiv.addClass('dark');
        }

        boxDiv.text(text);

        // Replay button only for assistant messages
        if (!isUser && audioBase64) {
            const replayBtn = $('<button>')
                .addClass('btn btn-sm ml-2 replay-btn')
                .html('<i class="fa fa-play-circle"></i>');

            replayBtn.on('click', function () {
                playAudio(audioBase64, this);
            });

            boxDiv.append(replayBtn);

            // Auto-play assistant audio
            playAudio(audioBase64, replayBtn);
        }

        msgDiv.append(boxDiv);
        messageList.append(msgDiv);

        // Auto-scroll
        chatWindow.animate(
            { scrollTop: chatWindow.prop('scrollHeight') },
            500
        );
    }
    // =====================
    // Scrollbar Visibility
    // =====================
    let scrollTimeout;
    chatWindow.on('scroll', function () {
        chatWindow.addClass('scrolling');
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            chatWindow.removeClass('scrolling');
        }, 1000); // Hide after 1 second of inactivity
    });


    let currentAudio = null;
    let currentAudioBtn = null;

    function playAudio(base64, btnInput = null) {
        // Normalize btn to raw DOM element (in case a jQuery object was passed)
        const btn = btnInput && btnInput.jquery ? btnInput[0] : btnInput;

        // If clicking the SAME button while playing -> Pause
        if (currentAudio && currentAudioBtn === btn) {
            if (!currentAudio.paused) {
                currentAudio.pause();
                updateBtnIcon(btn, 'play');
                return;
            } else {
                currentAudio.play();
                updateBtnIcon(btn, 'pause');
                return;
            }
        }

        // If something else is playing, stop it
        if (currentAudio) {
            currentAudio.pause();
            updateBtnIcon(currentAudioBtn, 'play');
        }

        // Start new audio
        currentAudio = new Audio("data:audio/mpeg;base64," + base64);
        currentAudioBtn = btn;

        currentAudio.onplay = () => updateBtnIcon(btn, 'pause');
        currentAudio.onpause = () => updateBtnIcon(btn, 'play');
        currentAudio.onended = () => {
            updateBtnIcon(btn, 'play');
            currentAudio = null;
            currentAudioBtn = null;
        };

        currentAudio.play();
    }

    function updateBtnIcon(btn, state) {
        if (!btn) return;
        const icon = state === 'pause' ? 'fa-pause-circle' : 'fa-play-circle';
        $(btn).html(`<i class="fa ${icon}"></i>`);
    }

    // =====================
    // Recording Logic
    // =====================
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendAudio(audioBlob);
            };

            mediaRecorder.start();
            isRecording = true;
            recordingStartTime = Date.now();

            recordBtn.addClass('recording');
            $('.instruction-text').text('Listening...Tap again to send!');

        } catch (err) {
            console.error('Mic error:', err);
            alert('Could not access microphone.');
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            recordingDuration = (Date.now() - recordingStartTime) / 1000;
            console.log(`Recording ended. Duration: ${recordingDuration.toFixed(2)}s`);

            recordBtn.removeClass('recording');
            $('.instruction-text').text('Tap the microphone to speak');
        }
    }

    // =====================
    // Voice Activity Detection (VAD)
    // =====================
    function hasActualSpeech(audioBlob) {
        return new Promise((resolve) => {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const reader = new FileReader();

            reader.onload = function (e) {
                audioContext.decodeAudioData(e.target.result, function (buffer) {
                    const samples = buffer.getChannelData(0);
                    let sum = 0;
                    let peakCount = 0;

                    // Calculate RMS (Root Mean Square) energy
                    for (let i = 0; i < samples.length; i++) {
                        sum += samples[i] * samples[i];
                        if (Math.abs(samples[i]) > 0.1) peakCount++;
                    }

                    const rms = Math.sqrt(sum / samples.length);
                    const speechRatio = peakCount / samples.length;

                    // Thresholds: RMS > 0.02 means some volume, speechRatio > 0.05 means varied audio
                    const hasSpeech = (rms > 0.02 && speechRatio > 0.05);

                    console.log(`VAD Check: RMS=${rms.toFixed(4)}, SpeechRatio=${speechRatio.toFixed(4)}, HasSpeech=${hasSpeech}`);
                    resolve(hasSpeech);
                });
            };

            reader.readAsArrayBuffer(audioBlob);
        });
    }

    // =====================
    // 2-Step API Orchestration
    // =====================
    async function sendAudio(blob) {
        expandChat();
        showLoading('user');

        try {
            // NEW: Voice Activity Detection - Check if there's actual speech BEFORE sending to API
            const hasSpeech = await hasActualSpeech(blob);
            if (!hasSpeech) {
                console.warn("VAD: No speech detected in audio");
                hideLoading();
                instructionText.text("No speech detected. Try speaking louder?");
                return;
            }

            // STEP 1: Get Transcription (STT)
            const sttData = new FormData();
            sttData.append('audio', blob, 'recording.wav');

            const sttRes = await fetch('/api/stt', { method: 'POST', body: sttData });
            const sttJson = await sttRes.json();

            // Handle API level errors (500, 400, etc.)
            if (!sttRes.ok || sttJson.error) {
                throw new Error(sttJson.error || "Speech recognition failed");
            }

            // SUCCESS Phase 1: Show your text and switch loading
            appendMessage('user', sttJson.user_text);
            showLoading('ai');

            // STEP 2: Get AI Response (LLM + TTS)
            const aiData = new FormData();
            aiData.append('text', sttJson.user_text);
            aiData.append('voice', voiceOptions.val());
            aiData.append('session_id', sessionId);

            const aiRes = await fetch('/api/ai_response', { method: 'POST', body: aiData });
            const aiJson = await aiRes.json();

            if (aiJson.error) throw new Error(aiJson.error);

            // SUCCESS Phase 2: Show AI reply
            hideLoading();
            appendMessage('assistant', aiJson.assistant_text, aiJson.audio_base64);

        } catch (err) {
            hideLoading();
            console.error('Pipeline error:', err);
            appendMessage('assistant', 'Error: ' + err.message);
        }
    }

    // =====================
    // Event Bindings
    // =====================
    recordBtn.on('click', function () {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });

});
