import Navbar from './Navbar';

interface LoadingScreenProps {
  message?: string;
}

export default function LoadingScreen({ message = "Loading..." }: LoadingScreenProps) {
  return (
    <>
      <Navbar />
      <div className="min-h-screen pt-16 bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 flex items-center justify-center">
        <div className="bg-white/10 backdrop-blur-lg rounded-lg p-8 flex flex-col items-center">
          <div className="relative w-24 h-24">
            {/* Outer spinning ring */}
            <div className="absolute inset-0 rounded-full border-4 border-white/20 animate-[spin_3s_linear_infinite]"></div>
            {/* Inner spinning ring */}
            <div className="absolute inset-2 rounded-full border-4 border-t-white/80 border-white/20 animate-[spin_2s_linear_infinite]"></div>
            {/* Center dot */}
            <div className="absolute inset-[38%] rounded-full bg-white/80 animate-pulse"></div>
          </div>
          <p className="text-white text-lg mt-6 font-medium animate-pulse">
            {message}
          </p>
        </div>
      </div>
    </>
  );
}
