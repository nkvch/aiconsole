import initSwc, { transform } from '@swc/wasm-web';

export const transpileCode = async (code: string) => {
  await initSwc();

  const transpiled = await transform(code, {
    jsc: { parser: { syntax: 'typescript', tsx: true } },
  });

  const finalCode = `${transpiled.code}\n\nreturn Component;`;

  return finalCode;
};
