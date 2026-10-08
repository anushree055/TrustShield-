export const scamTypes = [
  {icon:'🏦', name:'Banking Phishing', short:'Fake bank messages or sites that try to steal login, card or OTP details.', signs:['Urgent KYC/account warnings','Look-alike login links','Requests for OTP/PIN/password'], protect:'Open the official banking app yourself and never share OTP/PIN.'},
  {icon:'🔐', name:'OTP Scam', short:'Someone tricks you into sharing a one-time password or security code.', signs:['Asks for OTP on call/chat','Creates urgency','Claims to be support or bank staff'], protect:'Treat every OTP as private. Genuine staff should not ask you to reveal it.'},
  {icon:'💼', name:'Fake Job Scam', short:'Fraudulent recruiters offer jobs, then ask for fees or sensitive documents.', signs:['Registration/training fee','Personal email or chat-only recruiter','Very high salary with little screening'], protect:'Verify the job on the company careers page before paying or sending documents.'},
  {icon:'🎁', name:'Lottery / Prize Scam', short:'A fake prize or reward is used to demand fees, banking data or identity details.', signs:['Prize you never entered','Processing/tax fee','Pressure to claim quickly'], protect:'Do not pay to receive an unexpected prize.'},
  {icon:'📈', name:'Investment Scam', short:'Promises of guaranteed, unusually high or fast returns designed to trigger deposits.', signs:['Guaranteed returns','Urgent limited slot','Payment to personal wallet/account'], protect:'Verify registration and never invest under pressure.'},
  {icon:'🛍️', name:'Fake Shopping Scam', short:'Fraudulent stores or sellers use attractive offers to collect money or card data.', signs:['Extreme discounts','New or strange domain','Advance payment pressure'], protect:'Verify the seller independently and use trusted payment methods.'},
  {icon:'📦', name:'Delivery Scam', short:'Fake parcel messages ask for a small fee or personal details through an external link.', signs:['Unexpected delivery fee','Package held warning','Unfamiliar tracking link'], protect:'Check the order only in the courier or shopping app you already use.'},
  {icon:'💳', name:'UPI / Payment Scam', short:'Fraudsters misuse QR codes, collect requests and payment flows to make victims authorize transfers.', signs:['UPI PIN requested to receive money','Unknown collect request','Refund through QR code'], protect:'You do not enter a UPI PIN to receive money.'},
  {icon:'🎭', name:'Impersonation Scam', short:'A scammer pretends to be a friend, boss, official or known organization.', signs:['New number','Urgent money request','Tells you not to call'], protect:'Verify the identity using another trusted channel.'},
  {icon:'🖥️', name:'Tech Support Scam', short:'Fake support agents claim your device has a problem and ask for remote access or payment.', signs:['Remote access app request','Virus scare','Unexpected support call'], protect:'Do not grant remote access to unsolicited callers.'},
]

export const demoMessages = {
  'Banking Phishing':'Dear customer, your bank account will be suspended today because KYC has expired. Verify your account immediately at http://secure-bank-login.example.test and enter your OTP to continue.',
  'Fake Job Scam':'Congratulations! You are selected for a work from home job with salary ₹55,000. Pay a registration fee of ₹2,499 today and send your Aadhaar and bank details to confirm your position.',
  'OTP Scam':'Customer care here. We are processing your refund. Please share the OTP sent to your phone immediately so we can complete the transaction.',
  'Lottery Scam':'Congratulations! You won a ₹5,00,000 lottery prize. Pay a processing fee today to claim the reward before it expires.',
  'UPI Scam':'Your refund is ready. Scan this QR code and enter your UPI PIN to receive ₹4,999 immediately.',
  'Safe Message':'Reminder: your project meeting is tomorrow at 10:30 AM in Seminar Hall 2. Please bring the printed report.'
}
