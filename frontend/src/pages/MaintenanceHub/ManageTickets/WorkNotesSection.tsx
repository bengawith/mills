/*
  WorkNotesSection.tsx - MillDash Frontend Maintenance Ticket Work Notes Section

  This file implements the work notes section for a maintenance ticket in the MillDash maintenance hub using React and TypeScript. It provides a user interface for viewing, adding, and logging work notes associated with a ticket. The component manages note state, interacts with backend APIs for note creation, and uses custom UI components for a consistent and accessible layout.

  Key Features:
  - Uses React functional component with props for ticket ID, notes list, and note added callback.
  - Displays a scrollable log of work notes, sorted by creation time.
  - Allows users to add new notes with author attribution.
  - Submits new notes to backend and triggers parent refetch on success.
  - Displays toast notifications for success, error, and validation feedback.
  - Utilizes custom UI components (Card, Textarea, Input, Button, Label).
  - Responsive and visually appealing layout using Tailwind CSS utility classes.

  This component is essential for maintenance management, enabling collaborative tracking of work performed on machine issues.
*/

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
  // React Query client for cache management and invalidation
  const queryClient = useQueryClient();
  // Toast notification handler for user feedback
  const { toast } = useToast();
  // State for new note input
  const [newNote, setNewNote] = useState<string>('');
  // State for note author input
  const [noteAuthor, setNoteAuthor] = useState<string>('');

  /**
   * Mutation for adding a new work note to the ticket.
   * On success, clears input, triggers parent refetch, and shows success toast.
   * On error, displays error toast.
   */
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

  /**
   * Handles form submission for adding a new work note.
   * Validates input and triggers mutation.
   * @param e - React form event
   */
  const handleAddNote = (e: React.FormEvent<HTMLFormElement>): void => {
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
