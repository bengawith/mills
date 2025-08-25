import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { uploadTicketImage } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';

interface TicketImage {
  id: number;
  image_url: string;
  caption?: string;
}

interface ImageSectionProps {
  ticketId: number;
  images: TicketImage[];
  onImageUploaded: () => void;
}

const ImageSection: React.FC<ImageSectionProps> = ({ ticketId, images, onImageUploaded }) => {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const uploadImageMutation = useMutation({
    mutationFn: (file: File) => uploadTicketImage(ticketId, file),
    onSuccess: () => {
      setSelectedFile(null);
      onImageUploaded(); // Trigger refetch in parent
      toast({
        title: "Image Uploaded",
        description: "Image attached successfully.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to upload image.",
        variant: "destructive",
      });
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    } else {
      setSelectedFile(null);
    }
  };

  const handleUpload = (e: React.FormEvent) => {
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

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Attached Images</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 mb-4">
          {images.length > 0 ? (
            images.map((img) => (
              <div key={img.id} className="relative group">
                <img 
                  src={`http://localhost:8000/${img.image_url}`} // Adjust URL as needed
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
