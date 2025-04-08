
import { Button } from '../common/Button';

interface GithubLoginProps {
  onLogin: () => void;
}

export function GithubLogin({ onLogin }: GithubLoginProps) {
  return (
    <div className="mt-5 text-center">
      <p className="text-white mb-4">Please login with GitHub to continue</p>
      <Button onClick={onLogin} className="bg-gray-800 hover:bg-gray-700 text-white">
        <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0a12 12 0 00-3.8 23.4c.6.1.8-.3.8-.6v-2.2c-3.3.7-4-1.6-4-1.6-.5-1.3-1.3-1.6-1.3-1.6-1-.7.1-.7.1-.7 1.1 0 1.7 1.1 1.7 1.1 1 1.7 2.6 1.2 3.2.9.1-.7.4-1.2.7-1.5-2.4-.3-4.9-1.2-4.9-5.3 0-1.2.4-2.2 1.1-2.9-.1-.3-.5-1.4.1-2.9 0 0 .9-.3 3 1.1a10.5 10.5 0 015.5 0c2.1-1.4 3-1.1 3-1.1.6 1.5.2 2.6.1 2.9.7.7 1.1 1.7 1.1 2.9 0 4.1-2.5 5-4.9 5.3.4.3.7 1 .7 1.5v3.3c0 .3.2.7.8.6A12 12 0 0012 0z" />
        </svg>
        Login with GitHub
      </Button>
    </div>
  );
}
