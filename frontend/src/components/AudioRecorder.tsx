import { useState, useEffect } from 'react';
import { Mic, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { recordAudio } from '@/utils/audioUtils';

interface AudioRecorderProps {
  onRecordingComplete: (audioBlob: Blob) => void;
  isRecording: boolean;
  isComplete: boolean;
  label: string;
  disabled?: boolean;
}

export function AudioRecorder({
  onRecordingComplete,
  isRecording,
  isComplete,
  label,
  disabled = false,
}: AudioRecorderProps) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (isRecording) {
      setProgress(0);
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 2;
        });
      }, 100);
      return () => clearInterval(interval);
    }
  }, [isRecording]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative"
    >
      <button
        onClick={async () => {
          if (!isRecording && !isComplete && !disabled) {
            const blob = await recordAudio(5);
            onRecordingComplete(blob);
          }
        }}
        disabled={disabled || isRecording || isComplete}
        className={`relative w-full h-20 rounded-2xl transition-all duration-300 ${
          isComplete
            ? 'bg-success text-success-foreground'
            : isRecording
            ? 'bg-destructive text-destructive-foreground animate-pulse-ring'
            : 'glass-card hover:shadow-glow'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
      >
        <div className="flex items-center justify-between px-6">
          <span className="font-semibold text-lg">{label}</span>
          <AnimatePresence mode="wait">
            {isComplete ? (
              <motion.div
                key="check"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                exit={{ scale: 0 }}
              >
                <Check className="w-8 h-8" />
              </motion.div>
            ) : (
              <motion.div
                key="mic"
                initial={{ scale: 1 }}
                animate={isRecording ? { scale: [1, 1.2, 1] } : { scale: 1 }}
                transition={{ repeat: isRecording ? Infinity : 0, duration: 1 }}
              >
                <Mic className="w-8 h-8" />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        {isRecording && (
          <div className="absolute bottom-0 left-0 h-1 bg-accent rounded-b-2xl transition-all duration-100"
               style={{ width: `${progress}%` }} />
        )}
      </button>

      {isRecording && (
        <div className="flex gap-1 justify-center mt-3">
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              className="w-1 bg-accent rounded-full"
              animate={{
                height: [20, 40, 20],
              }}
              transition={{
                duration: 0.8,
                repeat: Infinity,
                delay: i * 0.1,
              }}
            />
          ))}
        </div>
      )}
    </motion.div>
  );
}
