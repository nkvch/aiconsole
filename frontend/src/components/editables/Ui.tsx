import { createSandbox } from '@/utils/transpilation/createSandbox';
import { transpileCode } from '@/utils/transpilation/transpileCode';
import { useState, ReactNode } from 'react';
import { CodeInput } from './assets/CodeInput';
import { Button } from '../common/Button';
import { FormGroup } from '../common/FormGroup';

const exampleCode = `const Component = () => {
  return <h2>Hi, I am a Component!</h2>;
}
`;

export const UI = () => {
  const [result, setResult] = useState<ReactNode | null>(null);
  const [code, setCode] = useState(exampleCode);
  const [error, setError] = useState('');

  const handleCodeChange = (code: string) => setCode(code);

  const handleSubmit = async () => {
    setError('');
    try {
      const finalCode = await transpileCode(code);

      const sandboxed = createSandbox(finalCode);

      if (sandboxed) {
        setResult(sandboxed());
      }
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <FormGroup className="flex flex-col w-full gap-[20px]">
      <CodeInput value={code} codeLanguage="javascript" onChange={handleCodeChange} label="React Code" />
      <Button onClick={handleSubmit} variant="secondary">
        Transpile
      </Button>
      {!!error && <div className="text-danger flex text-xs">Error: {error}</div>}
      {result}
    </FormGroup>
  );
};
