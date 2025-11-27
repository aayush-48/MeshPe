import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic } from 'lucide-react';
import { EnhancedButton } from './ui/enhanced-button';
import { Input } from './ui/input';
import { loginStart, loginVerify } from '@/utils/apiClient';
import { recordAudio } from '@/utils/audioUtils';
import { useAuth } from '@/context/AuthContext';
import { toast } from '@/hooks/use-toast';

export function LoginScreen() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [phone, setPhone] = useState('');
  const [challenge, setChallenge] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [language] = useState('english');

  const handleStartLogin = async () => {
    console.log("Start Login clicked. Phone:", phone);
    if (!phone) {
      console.log("No phone number entered");
      return;
    }

    try {
      console.log("Calling loginStart API...");
      const response = await loginStart(phone);
      console.log("API Response:", response);

      if (response.success && response.data) {
        console.log("Setting challenge:", response.data.challenge);
        setChallenge(response.data.challenge);
      } else {
        console.error("Login failed:", response.error);
        toast({
          title: 'Error',
          description: response.error || 'Failed to start login',
          variant: 'destructive',
        });
      }
    } catch (e) {
      console.error("Exception in handleStartLogin:", e);
    }
  };

  const handleRecordAndVerify = async () => {
    if (!challenge || isRecording) return;

    setIsRecording(true);
    try {
      const audioBlob = await recordAudio(5);
      setIsRecording(false);
      setIsVerifying(true);

      const formData = new FormData();
      formData.append('audio', audioBlob, 'voice.webm');
      formData.append('language', language);
      formData.append('user_id', phone);

      const response = await loginVerify(formData);
      setIsVerifying(false);

      if (response.success && response.data?.user) {
        setUser(response.data.user);
        toast({
          title: 'Welcome back!',
          description: 'Login successful',
        });
        navigate('/payment');
      } else {
        toast({
          title: 'Verification Failed',
          description: response.error || 'Voice verification failed',
          variant: 'destructive',
        });
        setChallenge(null);
      }
    } catch (error) {
      setIsRecording(false);
      setIsVerifying(false);
      toast({
        title: 'Error',
        description: 'Failed to record audio',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="min-h-screen gradient-secondary flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-lg glass-card rounded-3xl p-8 shadow-elevated"
      >
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Welcome Back</h1>
          <p className="text-muted-foreground">Login with your voice</p>
        </div>

        <AnimatePresence mode="wait">
          {!challenge ? (
            <motion.div
              key="phone"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-6"
            >
              <div>
                <label className="block text-sm font-medium mb-2">Phone Number</label>
                <Input
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+91 1234567890"
                  className="h-12 rounded-xl"
                />
              </div>

              <EnhancedButton
                variant="gradient"
                size="lg"
                className="w-full"
                onClick={handleStartLogin}
                disabled={!phone}
              >
                Start Login
              </EnhancedButton>

              <div className="text-center">
                <button
                  onClick={() => navigate('/signup')}
                  className="text-primary hover:underline text-sm"
                >
                  Don't have an account? Sign up
                </button>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="challenge"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-8"
            >
              <div className="text-center p-6 rounded-2xl bg-accent/10 border-2 border-accent">
                <p className="text-sm text-muted-foreground mb-2">Say this phrase:</p>
                <p className="text-2xl font-bold text-accent">{challenge}</p>
              </div>

              <div className="flex justify-center">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleRecordAndVerify}
                  disabled={isRecording || isVerifying}
                  className={`w-32 h-32 rounded-full flex items-center justify-center transition-all duration-300 ${isRecording
                      ? 'bg-destructive animate-pulse-ring'
                      : 'bg-accent hover:shadow-glow'
                    } disabled:opacity-50`}
                >
                  <Mic className="w-16 h-16 text-accent-foreground" />
                </motion.button>
              </div>

              <p className="text-center text-sm text-muted-foreground">
                {isRecording
                  ? 'Recording... (5 seconds)'
                  : isVerifying
                    ? 'Verifying your voice...'
                    : 'Tap to record'}
              </p>

              <EnhancedButton
                variant="ghost"
                size="sm"
                className="w-full"
                onClick={() => setChallenge(null)}
              >
                Back
              </EnhancedButton>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
