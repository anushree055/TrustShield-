from typing import Dict, List

BASE = {
    "Banking Phishing": {
        "immediate": "Do not open the supplied link or submit any banking details.",
        "protect": "Do not share OTP, PIN, CVV, password, or card details.",
        "verify": "Open your bank's official app or type its official website yourself.",
        "interacted": "If you entered credentials, change them immediately from the official app/site.",
        "recovery": "Contact your bank using the number on your card or official website and review recent transactions."
    },
    "OTP Scam": {
        "immediate": "Do not share the OTP or approve any unknown request.",
        "protect": "Keep OTPs, PINs and authentication codes private.",
        "verify": "Contact the service through its official app or website if the request seems genuine.",
        "interacted": "If you shared an OTP, secure the related account immediately.",
        "recovery": "Contact the bank/service provider and report unauthorized activity."
    },
    "Fake Job Scam": {
        "immediate": "Do not pay registration, interview, training, or equipment fees.",
        "protect": "Avoid sharing Aadhaar, PAN, bank details, or identity documents before verification.",
        "verify": "Check the role on the company's official careers page and verify the recruiter's company email domain.",
        "interacted": "Stop further payments or document sharing until the employer is independently verified.",
        "recovery": "Contact your bank if money was sent and save messages, receipts, and recruiter details as evidence."
    },
    "Lottery / Prize Scam": {
        "immediate": "Do not pay any fee to claim a prize you did not knowingly enter for.",
        "protect": "Do not share banking or identity information to receive the claimed reward.",
        "verify": "Verify the promotion on the organization's official website using contact details you find yourself.",
        "interacted": "Stop responding if the sender keeps asking for fees or personal information.",
        "recovery": "If money was sent, contact your payment provider quickly and preserve the conversation."
    },
    "Investment Scam": {
        "immediate": "Do not transfer money based on pressure or guaranteed-return claims.",
        "protect": "Do not share trading credentials, OTPs, or remote-access permissions.",
        "verify": "Check the company/adviser through official regulatory or company sources before investing.",
        "interacted": "Do not send additional money to unlock withdrawals or recover earlier payments.",
        "recovery": "Contact your bank/payment provider and keep transaction records and chat evidence."
    },
    "Fake Shopping Scam": {
        "immediate": "Avoid advance payment until the seller and website are independently verified.",
        "protect": "Do not reuse passwords or share card/OTP details outside a trusted checkout.",
        "verify": "Check the domain spelling, seller reputation, return policy, and independent reviews.",
        "interacted": "If you created an account with a reused password, change that password elsewhere too.",
        "recovery": "Contact your bank/card issuer if payment details were exposed or an unauthorized charge appears."
    },
    "Delivery Scam": {
        "immediate": "Do not pay a surprise delivery fee through an unsolicited link.",
        "protect": "Do not provide OTPs, card details, or account passwords to a delivery message sender.",
        "verify": "Open the courier's official app/site and check tracking using the real order number.",
        "interacted": "Close any suspicious payment page and change exposed credentials.",
        "recovery": "Contact the courier and payment provider through official channels if money was lost."
    },
    "UPI / Payment Scam": {
        "immediate": "Do not approve unknown collect requests or scan QR codes sent by strangers for receiving money.",
        "protect": "Never enter your UPI PIN to receive money and never share OTPs.",
        "verify": "Confirm the recipient name and payment purpose before authorizing any transfer.",
        "interacted": "If you approved a suspicious payment, contact your bank immediately.",
        "recovery": "Report the transaction through your bank/payment app and preserve the transaction ID."
    },
    "Impersonation Scam": {
        "immediate": "Pause the conversation and do not send money or sensitive information.",
        "protect": "Do not rely only on the display name, profile photo, or caller ID.",
        "verify": "Contact the person or organization using a separate, trusted channel you already know.",
        "interacted": "Tell the real person/organization if their identity appears to be misused.",
        "recovery": "Contact your bank/payment service if funds were transferred."
    },
    "Tech Support Scam": {
        "immediate": "Do not install remote-access software or allow unknown people to control your device.",
        "protect": "Do not share passwords, OTPs, payment details, or device access codes.",
        "verify": "Contact the product/company through its official support page.",
        "interacted": "Disconnect remote access, uninstall unknown remote-control tools, and change passwords from a trusted device.",
        "recovery": "Run a security scan and contact your bank if payment or banking details were exposed."
    },
    "Credential Theft": {
        "immediate": "Do not submit usernames, passwords, OTPs, PINs, or identity details.",
        "protect": "Use the official app/site and a unique password with multi-factor authentication.",
        "verify": "Check the domain carefully and navigate to the service independently.",
        "interacted": "Change the exposed password immediately and sign out of other sessions where possible.",
        "recovery": "Monitor the account for suspicious logins and contact official support if access was lost."
    },
}

DEFAULT = {
    "immediate": "Do not act on the request until you independently verify it.",
    "protect": "Do not share passwords, OTPs, PINs, banking information, or identity documents.",
    "verify": "Use the organization's official app, website, or known phone number rather than links in the message.",
    "interacted": "If you already clicked or replied, review what information you exposed and secure affected accounts.",
    "recovery": "If money or credentials were lost, contact the relevant bank/service provider promptly and keep evidence."
}

def recommendations_for(scam_type: str) -> List[Dict]:
    item = BASE.get(scam_type, DEFAULT)
    return [
        {"title": "Immediate Action", "text": item["immediate"]},
        {"title": "Protect Your Information", "text": item["protect"]},
        {"title": "Verify Safely", "text": item["verify"]},
        {"title": "If You Already Interacted", "text": item["interacted"]},
        {"title": "Recovery Step", "text": item["recovery"]},
    ]
