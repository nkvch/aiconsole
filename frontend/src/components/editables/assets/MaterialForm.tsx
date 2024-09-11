import { useEffect, useState } from 'react';

import { EditablesAPI } from '@/api/api/EditablesAPI';
import { FormGroup } from '@/components/common/FormGroup';
import { useAssetStore } from '@/store/editables/asset/useAssetStore';
import { Material, RenderedMaterial } from '@/types/editables/assetTypes';
import { MarkdownSupported } from '../MarkdownSupported';
import { CodeEditorLabelContent } from './CodeEditorLabelContent';
import { CodeInput } from './CodeInput';
import { useMaterialEditorContent } from './useMaterialEditorContent';
import RichTextEditor from './ProjectRich/RichTextEditor.tsx';
interface MaterialFormProps {
  material: Material;
  onChange: (field: string, value: any) => void;
}

export const MaterialForm = ({ material }: MaterialFormProps) => {
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const handleChange = (value: string) => setSelectedAsset({ ...material, usage: value });
  const [showPreview, setShowPreview] = useState(false);
  const [preview, setPreview] = useState<RenderedMaterial | undefined>(undefined);
  const previewValue = preview ? preview?.content.split('\\n').join('\n') : 'Generating preview...';
  const materialEditorContent = useMaterialEditorContent(material);

  useEffect(() => {
    if (!material) {
      return;
    }

    EditablesAPI.previewMaterial(material).then((preview) => {
      setPreview(preview);
    });
  }, [material]);

  const codePreviewConfig = {
    label: 'Preview of text to be injected into AI context',
    onChange: undefined,
    value: preview?.error ? preview.error : previewValue,
    codeLanguage: 'markdown',
  };

  const codeEditorSectionContent = showPreview ? codePreviewConfig : materialEditorContent;

  // @ts-ignore
  return (
      <>
        <FormGroup className="relative">
          <RichTextEditor
              className="min-h-[90px]"
              label="Usage"
              name="usage"
              value={material.usage}
              placeholder="Write text here"
              onChange={handleChange}
              helperText="Usage is used to help identify when this material should be used."
              fullWidth
          />
          <MarkdownSupported />
        </FormGroup>
        <FormGroup className="w-full flex flex-col" children={undefined}>
          <div className="flex-1">
            {codeEditorSectionContent ? (
                <CodeInput
                    label={codeEditorSectionContent.label}
                    labelContent={
                      <CodeEditorLabelContent showPreview={showPreview} onClick={() => setShowPreview((prev) => !prev)} />
                    }
                    labelSize="md"
                    value={codeEditorSectionContent.value}
                    codeLanguage={codeEditorSectionContent.codeLanguage}
                    onChange={codeEditorSectionContent.onChange}
                    readOnly={showPreview}
                />
            ) : null}
            <MarkdownSupported />
          </div>
        </FormGroup>
      </>
  );
};
