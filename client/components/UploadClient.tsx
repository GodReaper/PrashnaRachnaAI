'use client'

import { DocumentUpload } from "./DocumentUpload";

const UploadClient = () => {
  return (
<DocumentUpload
      onFileSelect={(file) => {
        console.log('File selected:', file.name);
      }}
      onUpload={(file) => {
        console.log('File uploaded:', file.name);
        // TODO: Implement actual upload logic in next tasks
      }}
    />
  )
}

export default UploadClient