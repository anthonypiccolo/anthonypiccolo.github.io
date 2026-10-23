---
title: "Easily encrypt email with Mailvelope"
date: 2013-08-24
category: Tech
draft: true
---
I recently started using <a href="http://www.openpgp.org/" target="_blank">OpenPGP</a> encryption on my email. And while most of my email doesn&#8217;t contain sensitive information worthy of encryption, I want to start taking better security measures when online. Or maybe I just don&#8217;t want the prying eyes of the NSA storing all of my email?

I&#8217;d like to think that every journalist and their source is encrypting email but most aren&#8217;t &#8212; leaving potential whistle blowers vulnerable. Journalists could easily provide their public key (which is required to send encrypted email to someone else) on their personal website making it readily available for sources to send encrypted email.

There are many guides out there to help you start encrypting your email but I&#8217;ll give a quick tutorial of what I do. For starters, who the hell uses a dedicated email client like Thunderbird or Outlook these days? I know I haven&#8217;t used one in a long time and I don&#8217;t plan on starting now. I, like most others use email in my web browser. I&#8217;ve been using Gmail for years and thankfully there&#8217;s a solution that works great for us who want to still use our favourite webmail service with better security. <a href="http://www.mailvelope.com/" target="_blank">Mailvelope</a> is the extension for Chrome and Firefox which makes this possible.

I&#8217;ll run through the quick and easy steps of setting everything up!

  1. Download the <a href="https://chrome.google.com/webstore/detail/mailvelope/kajibbejlbohfaggdiogboambcijhkke?hl=en" target="_blank">Mailvelope extension</a> from the Chrome web store.
  2. In the Mailvelope options, generate a private and public key by providing your full name, email address and creating a difficult passphrase that only you will know and remember. This passphrase will be used to decrypt email so you can read it! In the advanced section keep the algorithm set to &#8216;RSA&#8217; but change the key size to &#8216;4096 bits&#8217;. Now press &#8216;Submit&#8217; to generate your key.
  3. Your new key will now be in the &#8216;Display Keys&#8217; section of your key ring. As you get your friends to start encrypting their email, you&#8217;ll add their keys to this sections.
  4. You can add the public keys of the people you want to send and receive encrypted email with via the &#8216;Import Keys&#8217; section.
  5. To share your public key, simply select your own email in the key ring and click export. Make sure you choose your public and not private key. Never share your private key.
  6. In the security part of the Mailvelope settings there is an option to change where you compose your email. I usually choose to use the mail compose editor from my provider (Gmail) rather than using the Mailvelope editor.
  7. Now, go to Gmail and compose an email. You will notice in the top right of the compose window there is a Mailvelope key there. So, you&#8217;ll want to write your email, then click the key. You can now select anyone in your key ring. So find the person your wanting to send an encrypted email message, making sure you have their public key in your ring. Add them, hit the &#8216;OK&#8217; button and you&#8217;re done. Take that NSA!

Remember, metadata of email won&#8217;t be encrypted &#8212; so make sure subject lines are generalised. This is to maintain email protocols for sending and receiving email.

You can find a lot of public keys by searching the <a href="http://pgp.mit.edu/" target="_blank">MIT PGP Public Key Server</a>. My <a href="http://anthonyjamespiccolo.com/PGPKeyAnthonyPiccolo.asc" target="_blank">4096-bit RSA OpenPGP public key</a> can can be downloaded from this server. Hopefully journalists from major outlets can start providing their email and public key so potential sources can send encrypted email.

It has been reported that the NSA will pay more attention to email collected that is encrypted. Maybe they will eventually crack the encryption and see how mundane the email I send/receive is.

Oh and did you know that PGP stands for pretty good protection? How awesome is that!
