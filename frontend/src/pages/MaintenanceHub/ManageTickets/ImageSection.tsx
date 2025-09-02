// -----------------------------------------------------------------------------
// ImageSection.tsx
//
// This file defines the ImageSection React functional component, which is used
// within the ManageTickets module of the MaintenanceHub to display and upload
// images associated with a specific maintenance ticket. It provides a UI for
// listing all attached images, previewing them, and uploading new images to the
// backend. The component uses React Query for mutation, custom toast hooks for
// notifications, and UI components for consistent styling. It accepts the ticket
// ID, a list of images, and a callback for when a new image is uploaded.
//
// Props:
//   - ticketId: number (ID of the ticket to which images are attached)
//   - images: TicketImage[] (array of image objects with id, url, and optional caption)
//   - onImageUploaded: () => void (callback to trigger parent refresh after upload)
//
// Usage:
//   <ImageSection ticketId={...} images={...} onImageUploaded={...} />
// -----------------------------------------------------------------------------

import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { uploadTicketImage } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';


// Backend base URL for image retrieval
const backendUrl: string = 'http://localhost:8000';


/**
 * Represents an image attached to a ticket.
 */
export interface TicketImage {
  id: number;
  image_url: string;
  caption?: string;
}


/**
 * Props for the ImageSection component.
 */
export interface ImageSectionProps {
  ticketId: number;
  images: TicketImage[];
  onImageUploaded: () => void;
}


/**
 * ImageSection component displays all images attached to a ticket and provides
 * functionality to upload new images. Uses React Query for mutation and custom toast for notifications.
 */
const ImageSection: React.FC<ImageSectionProps> = ({ ticketId, images, onImageUploaded }: ImageSectionProps) => {
  // React Query client for cache management (not used directly here)
  const queryClient = useQueryClient();
  // Toast hook for notifications
  const { toast } = useToast();
  // State for the currently selected file to upload
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  /**
   * Mutation for uploading an image to the backend.
   */
  const uploadImageMutation = useMutation<File, unknown, File>({
    mutationFn: (file: File): Promise<any> => uploadTicketImage(ticketId, file),
    onSuccess: (): void => {
      setSelectedFile(null);
      onImageUploaded(); // Trigger refetch in parent
      toast({
        title: "Image Uploaded",
        description: "Image attached successfully.",
      });
    },
    onError: (error: any): void => {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to upload image.",
        variant: "destructive",
      });
    },
  });

  /**
   * Handles file input change event.
   * @param e - Change event from file input
   */
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    } else {
      setSelectedFile(null);
    }
  };

  /**
   * Handles the upload form submission.
   * @param e - Form event
   */
  const handleUpload = (e: React.FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    if (selectedFile) {
      uploadImageMutation.mutate(selectedFile);
    } else {
      toast({
        title: "No File Selected",
        description: "Please select an image to upload.",
        variant: "destructive",
      });
    }
  };

  // Render the card with attached images and upload form
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Attached Images</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Display attached images in a grid */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          {images.length > 0 ? (
            images.map((img: TicketImage) => (
              <div key={img.id} className="relative group">
                <img 
                  src={`${backendUrl}/${img.image_url}`}
                  alt={img.caption || `Image ${img.id}`}
                  className="w-full h-32 object-cover rounded-md"
                />
                {img.caption && <p className="text-xs text-muted-foreground mt-1">{img.caption}</p>}
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground col-span-2">No images attached.</p>
          )}
        </div>

        {/* Upload form for new images */}
        <form onSubmit={handleUpload} className="space-y-2">
          <div>
            <Label htmlFor="imageUpload">Upload New Image</Label>
            <Input id="imageUpload" type="file" accept="image/*" onChange={handleFileChange} />
          </div>
          <Button type="submit" size="sm" disabled={uploadImageMutation.isPending || !selectedFile}>
            {uploadImageMutation.isPending ? 'Uploading...' : 'Upload Image'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default ImageSection;
