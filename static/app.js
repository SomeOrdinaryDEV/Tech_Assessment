let isRecording = false;
let isPlaying = false;
let mediaRecorder = null;
let audioChunks = [];
let activeAudioPlayer = null;

const micBtn = document.getElementById('micBtn');
const statusBadge = document.getElementById('domainBadge');
const responseText = document.getElementById('responseText');
const alertCard = document.getElementById('alertCard');
const alertMsg = document.getElementById('alertMsg');

micBtn.addEventListener('click', () => {
  // Single-Tap Barge-In: Interrupt playback if audio is currently playing
  if (isPlaying) {
    stopAudioPlayback();
    startRecording();
    return;
  }

  if (isRecording) {
    stopRecording();
  } else {
    startRecording();
  }
});

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      await sendAudioToBackend(audioBlob);
    };

    mediaRecorder.start();
    isRecording = true;
    micBtn.classList.add('recording');
    micBtn.classList.remove('playing');
    statusBadge.innerText = 'सुन रहे हैं... (Listening)';
    responseText.innerText = 'अपनी बात बोलें...';
    alertCard.classList.remove('active');
  } catch (err) {
    console.error('Microphone access error:', err);
    statusBadge.innerText = 'माइक एक्सेस नहीं मिला';
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording) {
    mediaRecorder.stop();
    isRecording = false;
    micBtn.classList.remove('recording');
    statusBadge.innerText = 'प्रोसेस हो रहा है... (Processing)';
  }
}

async function sendAudioToBackend(audioBlob) {
  const formData = new FormData();
  formData.append('file', audioBlob, 'voice_input.webm');

  try {
    const res = await fetch('/api/process-audio', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();
    handlePipelineResponse(data);
  } catch (err) {
    console.error('Error sending audio:', err);
    statusBadge.innerText = 'कनेक्शन एरर (Connection Error)';
  }
}

function handlePipelineResponse(data) {
  statusBadge.innerText = `Domain: ${data.domain || 'General'}`;
  responseText.innerText = data.text_response || 'उत्तर उपलब्ध नहीं है।';

  if (data.is_emergency) {
    alertCard.classList.add('active');
    alertMsg.innerText = `🚨 ${data.text_response}`;
  }

  if (data.audio_b64) {
    playAudioResponse(data.audio_b64);
  }
}

function playAudioResponse(audioB64) {
  stopAudioPlayback();
  const audioUrl = `data:audio/mp3;base64,${audioB64}`;
  activeAudioPlayer = new Audio(audioUrl);

  isPlaying = true;
  micBtn.classList.add('playing');
  statusBadge.innerText = 'उत्तर बोल रहे हैं... (Tap to interrupt)';

  activeAudioPlayer.onended = () => {
    stopAudioPlayback();
  };

  activeAudioPlayer.play().catch((err) => {
    console.warn('Audio autoplay prevented:', err);
    stopAudioPlayback();
  });
}

function stopAudioPlayback() {
  if (activeAudioPlayer) {
    activeAudioPlayer.pause();
    activeAudioPlayer.currentTime = 0;
    activeAudioPlayer = null;
  }
  isPlaying = false;
  micBtn.classList.remove('playing');
  statusBadge.innerText = 'बोलने के लिए बटन दबाएं (Tap to Speak)';
}
