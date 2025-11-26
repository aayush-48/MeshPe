import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AudioRecorder } from './AudioRecorder';
import { EnhancedButton } from './ui/enhanced-button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { signup } from '@/utils/apiClient';
import { toast } from '@/hooks/use-toast';

export function SignupScreen() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [language, setLanguage] = useState('english');
  const [recordings, setRecordings] = useState<(Blob | null)[]>([null, null, null]);
  const [recordingStates, setRecordingStates] = useState([false, false, false]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleRecording = (index: number, blob: Blob) => {
    const newRecordings = [...recordings];
    newRecordings[index] = blob;
    setRecordings(newRecordings);

    const newStates = [...recordingStates];
    newStates[index] = false;
    setRecordingStates(newStates);
  };

  const startRecording = (index: number) => {
    const newStates = [...recordingStates];
    newStates[index] = true;
    setRecordingStates(newStates);
  };

  const allRecordingsComplete = recordings.every((r) => r !== null);
  const canSubmit = name && phone && allRecordingsComplete && !isSubmitting;

  const handleSubmit = async () => {
    if (!canSubmit) return;

    setIsSubmitting(true);
    const formData = new FormData();
    formData.append('name', name);
    formData.append('phone', phone);
    formData.append('language', language);
    recordings.forEach((blob, idx) => {
      if (blob) formData.append(`audio_${idx + 1}`, blob, `sample_${idx + 1}.webm`);
    });

    const response = await signup(formData);
    setIsSubmitting(false);

    if (response.success) {
      toast({
        title: 'Success!',
        description: 'Account created successfully. Please log in.',
      });
      navigate('/login');
    } else {
      toast({
        title: 'Signup Failed',
        description: response.error || 'An error occurred during signup',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="min-h-screen gradient-primary flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-2xl glass-card rounded-3xl p-8 shadow-elevated"
      >
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Create Account</h1>
          <p className="text-muted-foreground">Set up your voice-based authentication</p>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Full Name</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your name"
              className="h-12 rounded-xl"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Phone Number</label>
            <Input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+91 1234567890"
              className="h-12 rounded-xl"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Language</label>
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger className="h-12 rounded-xl">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="english">English</SelectItem>
                <SelectItem value="hindi">Hindi</SelectItem>
                <SelectItem value="marathi">Marathi</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-3">
            <label className="block text-sm font-medium">Voice Samples</label>
            <p className="text-sm text-muted-foreground mb-4">
              Record three 5-second voice samples for authentication
            </p>
            {[0, 1, 2].map((idx) => (
              <AudioRecorder
                key={idx}
                label={`Sample ${idx + 1}`}
                isRecording={recordingStates[idx]}
                isComplete={recordings[idx] !== null}
                onRecordingComplete={(blob) => handleRecording(idx, blob)}
              />
            ))}
          </div>

          <EnhancedButton
            variant="gradient"
            size="lg"
            className="w-full"
            disabled={!canSubmit}
            onClick={handleSubmit}
          >
            {isSubmitting ? 'Creating Account...' : 'Create Account'}
          </EnhancedButton>

          <div className="text-center">
            <button
              onClick={() => navigate('/login')}
              className="text-primary hover:underline text-sm"
            >
              Already have an account? Login
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
