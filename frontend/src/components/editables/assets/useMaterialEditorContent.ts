import { useAssetStore } from '@/store/editables/asset/useAssetStore';
import { MaterialContentType, Material } from '@/types/editables/assetTypes';

interface MaterialConfig {
  type: MaterialContentType;
  label: string;
  value: string;
  onChange: (value: string) => void;
  codeLanguage?: string;
}

export const useMaterialEditorContent = (material?: Material) => {
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);

  if (!material) return null;

  const setAsset = (assetName: string) => (value: string) =>
    setSelectedAsset({
      ...material,
      [assetName]: value,
    } as Material);

  const materialConfigs: MaterialConfig[] = [
    {
      type: 'static_text',
      label: 'Text',
      value: material.content,
      onChange: setAsset('content'),
      codeLanguage: 'markdown',
    },
    {
      type: 'dynamic_text',
      label: 'Python function returning dynamic text',
      value: material.content,
      onChange: setAsset('content'),
      codeLanguage: 'python',
    },
    {
      type: 'api',
      label: 'API Module',
      value: material.content,
      onChange: setAsset('content'),
    },
  ];

  const currentMaterialEditorContent = materialConfigs.find(({ type }) => material.content_type === type);

  return currentMaterialEditorContent;
};
