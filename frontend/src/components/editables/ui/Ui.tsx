import { createSandbox } from '@/utils/transpilation/createSandbox';
import { transpileCode } from '@/utils/transpilation/transpileCode';
import { useState, ReactNode, useCallback } from 'react';
import { CodeInput } from '../assets/CodeInput';
import { Button } from '../../common/Button';
import { FormGroup } from '../../common/FormGroup';
import { GenUIAPI } from '@/api/api/GenUIAPI';
import { CodeEditorLabelContent } from '../assets/CodeEditorLabelContent';

interface ApiResponse {
  code: string;
}

const DEFAULT_CODE = `function Component() {
  return (
    <div>
      <h1>Hello, World!</h1>
    </div>
  );
}`;

export const UI = () => {
  const [result, setResult] = useState<ReactNode | null>(null);
  const [prompt, setPrompt] = useState('Show a clock');
  const [code, setCode] = useState(DEFAULT_CODE);
  const [error, setError] = useState('');
  const [showPreview, setShowPreview] = useState(true);

  const handlePromptChange = (code: string) => setPrompt(code);

  const handleCodeChange = (code: string) => setCode(code);

  const handleSubmitCode = useCallback(async (code: string) => {
    setError('');
    try {
      const finalCode = await transpileCode(code);
      const sandbox = createSandbox(finalCode);
      setResult(sandbox);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  const handleSubmitPrompt = useCallback(async () => {
    setResult('');
    setError('');
    const response = await GenUIAPI.generateCode(prompt);

    const code = ((await response.json()) as ApiResponse).code;

    setCode(code);
    handleSubmitCode(code);
  }, [prompt, handleSubmitCode]);

  return (
    <FormGroup className="flex flex-col w-full gap-[20px]">
      <CodeInput
        value={showPreview ? <div className="p-4">{result}</div> : code}
        labelContent={
          <CodeEditorLabelContent
            showPreview={showPreview}
            onClick={() => {
              handleSubmitCode(code);
              setShowPreview((prev) => !prev);
            }}
          />
        }
        codeLanguage="javascript"
        onChange={handleCodeChange}
        label="Component"
        readOnly={showPreview}
      />
      {!!error && <div className="text-danger flex text-xs">Error: {error}</div>}

      <CodeInput value={prompt} codeLanguage="markdown" onChange={handlePromptChange} label="Prompt" />
      <Button onClick={handleSubmitPrompt} variant="secondary">
        Fix
      </Button>
    </FormGroup>
  );
};
