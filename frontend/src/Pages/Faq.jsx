import SimplePageLayout from '../components/SimplePageLayout';
import { useState } from 'react';

const faqData = [
  {
    q: "What is an IMEI number and how do I find it?",
    a: "The IMEI (International Mobile Equipment Identity) is a unique 15-digit number that identifies your specific mobile device. It's like a fingerprint for your phone. The easiest way to find it is by dialing *#06# on your phone's keypad. You can also find it in your phone's settings (usually under \"About Phone\" -> \"Status\") or printed on the original box."
  },
  {
    q: "Can I report my stolen phone directly on this website?",
    a: "No. To ensure the integrity and accuracy of our database, all reports must be filed in person at an authorized Nigerian Police station. This allows officers to verify proof of ownership and collect an official statement, which prevents fraudulent reports. We act as the central database for these verified police reports."
  },
  {
    q: "Is there a fee to report a stolen phone?",
    a: "Yes, there is a small administrative fee payable at the police station when you file an official report. This fee helps cover the costs of running and maintaining this secure national platform, ensuring it remains a reliable and long-term resource. The public IMEI check service, however, is always free."
  },
  {
    q: "What should I do if a phone I'm about to buy is listed as stolen?",
    a: "Do not proceed with the purchase. We advise you to thank the seller for their time and walk away. You can optionally and discreetly inform the seller that the device is flagged in the national database. For your own safety, do not attempt to confront the seller or confiscate the device yourself. You can report the encounter to the nearest police station if you feel it is safe to do so."
  },
  {
    q: "What happens if my phone is recovered?",
    a: "If your phone is recovered, you should return to the police station where you filed the initial report. They can update the status of your device in our system to \"Recovered.\" This will remove the \"stolen\" flag from your IMEI, allowing the device to be used or sold legally in the future."
  }
];

const ChevronDownIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" /></svg>`;

function FaqContent() {
  const [openIndex, setOpenIndex] = useState(null);

  const toggleAnswer = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <>
      <h1>Frequently Asked Questions</h1>
      <div id="faq-accordion" className="space-y-4 mt-8">
        {faqData.map((item, index) => (
          <div key={index} className="faq-item">
            <button
              onClick={() => toggleAnswer(index)}
              className="faq-question w-full flex justify-between items-center text-left p-4 bg-white border rounded-lg shadow-sm hover:bg-gray-50 focus:outline-none"
            >
              <span className="font-semibold text-gray-800">{item.q}</span>
              <span dangerouslySetInnerHTML={{ __html: ChevronDownIcon }} className={openIndex === index ? 'rotate-180' : ''} />
            </button>
            <div className={`faq-answer ${openIndex === index ? 'open' : ''}`}>
              <div className="p-4 bg-gray-50 border-t">
                <p>{item.a}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

export default function Faq() {
  return <SimplePageLayout content={<FaqContent />} />;
}