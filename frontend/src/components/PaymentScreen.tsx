import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Menu, LogOut, Users, CheckCircle } from 'lucide-react';
import { EnhancedButton } from './ui/enhanced-button';
import { initiatePayment, confirmPayment, logout as apiLogout } from '@/utils/apiClient';
import { recordAudio } from '@/utils/audioUtils';
import { useAuth } from '@/context/AuthContext';
import { toast } from '@/hooks/use-toast';

export function PaymentScreen() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [isRecording, setIsRecording] = useState(false);
  const [isConfirmRecording, setIsConfirmRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentInfo, setPaymentInfo] = useState<any>(null);
  const [rawText, setRawText] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [phase, setPhase] = useState<'idle' | 'review' | 'done'>('idle');

  const handleLogout = async () => {
    await apiLogout();
    logout();
    navigate('/login');
  };
  const handleRecordPayment = async () => {
    if (isRecording || isConfirmRecording || phase !== 'idle') return;

    setIsRecording(true);
    try {
      const audioBlob = await recordAudio(10);
      setIsRecording(false);
      setIsProcessing(true);

      const formData = new FormData();
      formData.append('audio', audioBlob, 'payment.webm');
      formData.append('language', user?.language || 'english');
      if (user?.id) {
        formData.append('user_id', user.id);
      }

      const response = await initiatePayment(formData);
      setIsProcessing(false);

      if (response.success && response.data) {
        setPaymentInfo(response.data.payment_info);
        setRawText(response.data.raw_text || null);
        setPhase('review');
      } else {
        toast({
          title: 'Payment Failed',
          description: response.error || 'Could not parse payment command',
          variant: 'destructive',
        });
      }
    } catch (error) {
      setIsRecording(false);
      setIsProcessing(false);
      toast({
        title: 'Error',
        description: 'Failed to process payment',
        variant: 'destructive',
      });
    }
  };

  const handleConfirmAndSend = async () => {
    if (!paymentInfo || isConfirmRecording || isProcessing || phase !== 'review') return;
    setIsConfirmRecording(true);
    try {
      const audioBlob = await recordAudio(3);
      setIsConfirmRecording(false);
      setIsProcessing(true);

      const formData = new FormData();
      formData.append('audio', audioBlob, 'confirm.webm');
      formData.append('language', user?.language || 'english');
      if (user?.id) {
        formData.append('user_id', user.id);
      }
      formData.append('receiver_name', paymentInfo.receiver_name);
      formData.append('amount', String(paymentInfo.amount));

      const response = await confirmPayment(formData);
      setIsProcessing(false);

      if (response.success && response.data) {
        setShowSuccess(true);
        setPhase('done');
        setTimeout(() => {
          setShowSuccess(false);
          setPaymentInfo(null);
          setRawText(null);
          setPhase('idle');
        }, 3000);
      } else {
        toast({
          title: 'Confirmation Failed',
          description: response.error || 'Voice or liveness verification failed',
          variant: 'destructive',
        });
      }
    } catch (error) {
      setIsConfirmRecording(false);
      setIsProcessing(false);
      toast({
        title: 'Error',
        description: 'Failed to process confirmation',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="min-h-screen gradient-primary">
      {/* Header */}
      <header className="glass-card border-b border-border/20">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <button onClick={() => navigate('/contacts')} className="p-2 hover:bg-accent/10 rounded-lg">
            <Menu className="w-6 h-6" />
          </button>
          <div className="text-center">
            <p className="text-sm text-muted-foreground">Welcome</p>
            <p className="font-semibold">{user?.name}</p>
          </div>
          <button onClick={handleLogout} className="p-2 hover:bg-destructive/10 rounded-lg text-destructive">
            <LogOut className="w-6 h-6" />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <AnimatePresence mode="wait">
          {!paymentInfo ? (
            <motion.div
              key="recorder"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-2xl mx-auto"
            >
              <div className="glass-card rounded-3xl p-8 shadow-elevated text-center">
                <h2 className="text-3xl font-bold mb-4">Make a Payment</h2>
                <p className="text-muted-foreground mb-8">
                  Say your payment command
                  <br />
                  <span className="text-sm italic">Example: "Pay Simran 100 rupees"</span>
                </p>

                <div className="flex justify-center mb-6">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleRecordPayment}
                    disabled={isRecording || isConfirmRecording || isProcessing || phase !== 'idle'}
                    className={`w-40 h-40 rounded-full flex items-center justify-center transition-all duration-300 ${isRecording
                        ? 'bg-destructive animate-pulse-ring'
                        : 'bg-accent hover:shadow-glow'
                      } disabled:opacity-50`}
                  >
                    <Mic className="w-20 h-20 text-accent-foreground" />
                  </motion.button>
                </div>

                <p className="text-sm text-muted-foreground">
                  {isRecording
                    ? 'Recording... (10 seconds)'
                    : isProcessing
                      ? 'Processing payment...'
                      : 'Tap to start recording your payment command'}
                </p>

                {isRecording && (
                  <div className="flex gap-2 justify-center mt-6">
                    {[...Array(5)].map((_, i) => (
                      <motion.div
                        key={i}
                        className="w-2 bg-accent rounded-full"
                        animate={{
                          height: [30, 60, 30],
                        }}
                        transition={{
                          duration: 0.8,
                          repeat: Infinity,
                          delay: i * 0.1,
                        }}
                      />
                    ))}
                  </div>
                )
                }
              </div >

              <div className="mt-6 text-center">
                <EnhancedButton
                  variant="glass"
                  size="lg"
                  onClick={() => navigate('/contacts')}
                  className="gap-3"
                >
                  <Users className="w-5 h-5" />
                  Manage Contacts
                </EnhancedButton>
              </div>
            </motion.div >
          ) : (
            <motion.div
              key="payment-info"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="max-w-lg mx-auto"
            >
              <div className="glass-card rounded-3xl p-8 shadow-elevated">
                {showSuccess ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="text-center"
                  >
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 0.5 }}
                    >
                      <CheckCircle className="w-24 h-24 text-success mx-auto mb-4" />
                    </motion.div>
                    <h2 className="text-3xl font-bold text-success mb-2">Payment Sent!</h2>
                    <p className="text-muted-foreground">Transaction completed successfully</p>
                  </motion.div>
                ) : (
                  <div className="space-y-6">
                    <div className="text-center">
                      <h3 className="text-2xl font-bold mb-4">Payment Details</h3>
                    </div>

                    <div className="space-y-4">
                      <div className="p-4 rounded-xl bg-muted/50">
                        <p className="text-sm text-muted-foreground">To</p>
                        <p className="text-xl font-semibold">{paymentInfo.receiver_name}</p>
                      </div>

                      <div className="p-4 rounded-xl bg-muted/50">
                        <p className="text-sm text-muted-foreground">Amount</p>
                        <p className="text-3xl font-bold text-primary">
                          {paymentInfo.currency} {paymentInfo.amount}
                        </p>
                      </div>

                      {rawText && (
                        <div className="p-4 rounded-xl bg-muted/50">
                          <p className="text-sm text-muted-foreground">You said</p>
                          <p className="text-base font-medium break-words">&ldquo;{rawText}&rdquo;</p>
                        </div>
                      )}

                      <div className="mt-4 text-center space-y-4">
                        <p className="text-sm text-muted-foreground">
                          Say <span className="font-semibold">"yes"</span> to confirm this payment.
                        </p>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={handleConfirmAndSend}
                          disabled={isConfirmRecording || isProcessing || phase !== 'review'}
                          className={`w-32 h-32 rounded-full flex items-center justify-center transition-all duration-300 ${isConfirmRecording
                            ? 'bg-destructive animate-pulse-ring'
                            : 'bg-accent hover:shadow-glow'
                            } disabled:opacity-50`}
                        >
                          <Mic className="w-16 h-16 text-accent-foreground" />
                        </motion.button>
                        <p className="text-xs text-muted-foreground">
                          {isConfirmRecording
                            ? 'Recording confirmation... (3 seconds)'
                            : isProcessing && phase === 'review'
                              ? 'Verifying your voice and liveness...'
                              : 'Tap to confirm with your voice'}
                        </p>
                      </div>
                    </div>

                    <EnhancedButton
                      variant="ghost"
                      className="w-full"
                      onClick={() => {
                        setPaymentInfo(null);
                        setRawText(null);
                        setPhase('idle');
                      }}
                    >
                      Cancel
                    </EnhancedButton>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence >
      </div >
    </div >
  );
}
