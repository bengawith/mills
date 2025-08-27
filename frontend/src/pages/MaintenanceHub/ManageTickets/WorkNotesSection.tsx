import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { addWorkNote } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { format } from 'date-fns';
import { useToast } from '@/hooks/use-toast';

interface WorkNote {
  id: number;
  note: string;
  author: string;
  created_at: string;
}

interface WorkNotesSectionProps {
  ticketId: number;
  workNotes: WorkNote[];
  onNoteAdded: () => void;
}

const WorkNotesSection: React.FC<WorkNotesSectionProps> = ({ ticketId, workNotes, onNoteAdded }) => {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [newNote, setNewNote] = useState('');
  const [noteAuthor, setNoteAuthor] = useState('');

  const addNoteMutation = useMutation({
    mutationFn: (noteData: { note: string; author: string }) => addWorkNote(ticketId, noteData),
    onSuccess: () => {
      setNewNote('');
      setNoteAuthor('');
      onNoteAdded(); // Trigger refetch in parent
      toast({
        title: "Note Added",
        description: "Work note added successfully.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to add note.",
        variant: "destructive",
      });
    },
  });

  const handleAddNote = (e: React.FormEvent) => {
    e.preventDefault();
    if (newNote.trim() && noteAuthor.trim()) {
      addNoteMutation.mutate({ note: newNote, author: noteAuthor });
    } else {
      toast({
        title: "Validation Error",
        description: "Note and author cannot be empty.",
        variant: "destructive",
      });
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Work Notes Log</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 mb-4 max-h-60 overflow-y-auto">
          {workNotes.length > 0 ? (
            workNotes.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()).map((note) => (
              <div key={note.id} className="border-b pb-2 last:border-b-0">
                <p className="text-sm font-semibold">{note.author} ({format(new Date(note.created_at), 'PPP p')}):</p>
                <p className="text-sm ml-2">{note.note}</p>
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No work notes yet.</p>
          )}
        </div>

        <form onSubmit={handleAddNote} className="space-y-2">
          <div>
            <Label htmlFor="newNote">New Note</Label>
            <Textarea id="newNote" value={newNote} onChange={(e) => setNewNote(e.target.value)} rows={3} />
          </div>
          <div>
            <Label htmlFor="noteAuthor">Your Name</Label>
            <Input id="noteAuthor" value={noteAuthor} onChange={(e) => setNoteAuthor(e.target.value)} />
          </div>
          <Button type="submit" size="sm" disabled={addNoteMutation.isPending}>
            {addNoteMutation.isPending ? 'Adding...' : 'Add Note'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default WorkNotesSection;
