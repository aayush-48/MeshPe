export async function recordAudio(durationSeconds: number): Promise<Blob> {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

  // Prefer an explicit, widely supported audio/webm format when possible.
  let options: MediaRecorderOptions = {};
  if (typeof MediaRecorder !== 'undefined') {
    if (MediaRecorder.isTypeSupported?.('audio/webm;codecs=opus')) {
      options.mimeType = 'audio/webm;codecs=opus';
    } else if (MediaRecorder.isTypeSupported?.('audio/webm')) {
      options.mimeType = 'audio/webm';
    }
  }

  const mediaRecorder = new MediaRecorder(stream, options);
  const chunks: Blob[] = [];

  mediaRecorder.ondataavailable = (e) => {
    if (e.data && e.data.size > 0) {
      chunks.push(e.data);
    }
  };

  return new Promise((resolve, reject) => {
    mediaRecorder.onstop = () => {
      try {
        stream.getTracks().forEach((track) => track.stop());
        const blob = new Blob(chunks, { type: options.mimeType || 'audio/webm' });
        console.log("Recorded audio blob size:", blob.size);
        if (blob.size === 0) {
          reject(new Error("Recorded audio is empty. Please check your microphone."));
          return;
        }
        resolve(blob);
      } catch (err) {
        reject(err);
      }
    };

    mediaRecorder.onerror = (error) => {
      stream.getTracks().forEach((track) => track.stop());
      reject(error);
    };

    // Use a timeslice so data is flushed periodically; this avoids some browsers
    // never emitting data if only a single stop() is used.
    mediaRecorder.start(500);

    setTimeout(() => {
      if (mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
      }
    }, durationSeconds * 1000);
  });
}

export function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result as string;
      resolve(base64.split(',')[1]);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}
