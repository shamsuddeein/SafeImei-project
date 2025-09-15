import SimplePageLayout from '../components/SimplePageLayout';

const contactContent = `
  <h1>Contact Us</h1>
  <p>We're here to help. Whether you have a question about our service, a suggestion, or a partnership inquiry, please feel free to reach out. Please note: to report a stolen phone, you must visit an authorized police station in person.</p>
  <form id="contact-form" class="mt-8 space-y-6">
    <div>
      <label for="contact-name" class="block text-sm font-medium text-gray-700">Full Name</label>
      <div class="mt-1"><input type="text" id="contact-name" required class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"></div>
    </div>
    <div>
      <label for="contact-email" class="block text-sm font-medium text-gray-700">Email Address</label>
      <div class="mt-1"><input type="email" id="contact-email" required class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"></div>
    </div>
    <div>
      <label for="contact-message" class="block text-sm font-medium text-gray-700">Message</label>
      <div class="mt-1"><textarea id="contact-message" rows="4" required class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"></textarea></div>
    </div>
    <div>
      <button type="submit" class="w-full flex justify-center py-3 px-4 border rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">Send Message</button>
    </div>
  </form>
`;

export default function Contact({ showModal }) {
  const handleContactSubmit = (e) => {
    e.preventDefault();
    showModal('Message Sent!', 'Thank you for contacting us. We will get back to you shortly.');
    e.target.reset();
  };

  return <SimplePageLayout content={<div dangerouslySetInnerHTML={{ __html: contactContent }} />} onSubmit={handleContactSubmit} />;
}