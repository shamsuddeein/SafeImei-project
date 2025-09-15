import { useEffect } from 'react';

export default function Auth({ setLoggedIn, navigateTo }) {
  const handleAuth = (e) => {
    e.preventDefault();
    setLoggedIn(true);
    navigateTo('dashboard');
  };

  useEffect(() => {
    const otpInputs = document.querySelectorAll('.otp-input');
    otpInputs.forEach((input, index) => {
      input.addEventListener('keydown', (e) => {
        if (e.key >= 0 && e.key <= 9) {
          input.value = '';
          setTimeout(() => otpInputs[index + 1]?.focus(), 10);
        } else if (e.key === 'Backspace') {
          setTimeout(() => otpInputs[index - 1]?.focus(), 10);
        }
      });
    });
    otpInputs[0]?.focus();
  }, []);

  return (
    <div className="page min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Two-Factor Authentication</h2>
        <p className="mt-2 text-center text-sm text-gray-600">Enter the 6-digit code.</p>
      </div>
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-lg sm:rounded-lg sm:px-10">
          <form onSubmit={handleAuth}>
            <div className="flex justify-center gap-2 md:gap-4 mb-6">
              {[...Array(6)].map((_, i) => (
                <input key={i} type="text" maxLength="1" className="otp-input w-12 h-14 md:w-14 md:h-16 text-center text-2xl font-semibold border border-gray-300 rounded-lg" required />
              ))}
            </div>
            <button type="submit" className="w-full flex justify-center py-2 px-4 border rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">Verify</button>
          </form>
        </div>
      </div>
    </div>
  );
}