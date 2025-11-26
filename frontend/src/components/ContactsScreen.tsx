import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Plus, User } from 'lucide-react';
import { EnhancedButton } from './ui/enhanced-button';
import { Input } from './ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { getContacts, addContact } from '@/utils/apiClient';
import { toast } from '@/hooks/use-toast';
import { useAuth } from '@/context/AuthContext';

interface Contact {
  name: string;
  id: string;
}

export function ContactsScreen() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newContactName, setNewContactName] = useState('');
  const [newContactId, setNewContactId] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    if (!user?.id) return;
    const response = await getContacts(user.id);
    if (response.success && response.data) {
      setContacts(response.data.contacts);
    }
  };

  const handleAddContact = async () => {
    if (!newContactName || !newContactId) return;
    if (!user?.id) {
      toast({
        title: 'Not logged in',
        description: 'You must be logged in to add contacts.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    const response = await addContact(user.id, newContactName, newContactId);
    setIsLoading(false);

    if (response.success) {
      toast({
        title: 'Contact Added',
        description: `${newContactName} has been added to your contacts`,
      });
      setNewContactName('');
      setNewContactId('');
      setIsDialogOpen(false);
      loadContacts();
    } else {
      toast({
        title: 'Error',
        description: response.error || 'Failed to add contact',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="min-h-screen gradient-secondary">
      {/* Header */}
      <header className="glass-card border-b border-border/20">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <button onClick={() => navigate('/payment')} className="p-2 hover:bg-accent/10 rounded-lg">
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-bold">Contacts</h1>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <button className="p-2 hover:bg-accent/10 rounded-lg">
                <Plus className="w-6 h-6" />
              </button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Add New Contact</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Contact Name</label>
                  <Input
                    value={newContactName}
                    onChange={(e) => setNewContactName(e.target.value)}
                    placeholder="Enter name"
                    className="h-12 rounded-xl"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Contact ID</label>
                  <Input
                    value={newContactId}
                    onChange={(e) => setNewContactId(e.target.value)}
                    placeholder="Enter phone or ID"
                    className="h-12 rounded-xl"
                  />
                </div>
                <EnhancedButton
                  variant="gradient"
                  size="lg"
                  className="w-full"
                  onClick={handleAddContact}
                  disabled={!newContactName || !newContactId || isLoading}
                >
                  {isLoading ? 'Adding...' : 'Add Contact'}
                </EnhancedButton>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </header>

      {/* Contacts List */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {contacts.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card rounded-3xl p-12 text-center shadow-card"
            >
              <User className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No Contacts Yet</h3>
              <p className="text-muted-foreground mb-6">
                Add contacts to quickly make payments
              </p>
              <EnhancedButton variant="gradient" onClick={() => setIsDialogOpen(true)}>
                <Plus className="w-5 h-5 mr-2" />
                Add Your First Contact
              </EnhancedButton>
            </motion.div>
          ) : (
            <div className="grid gap-4">
              {contacts.map((contact, index) => (
                <motion.div
                  key={contact.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="glass-card rounded-2xl p-6 shadow-card hover:shadow-glow transition-all cursor-pointer"
                  onClick={() => {
                    toast({
                      title: 'Contact Selected',
                      description: `You can now say "Pay ${contact.name}" to send money`,
                    });
                  }}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-primary flex items-center justify-center">
                      <User className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{contact.name}</h3>
                      <p className="text-sm text-muted-foreground">{contact.id}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
