<template>
  <div class="min-h-screen bg-[#0a0a0f] pt-32 pb-20">
    <div class="container mx-auto px-4 max-w-4xl">
      <h1 class="text-4xl font-bold text-white mb-8">Cookie Policy</h1>

      <div class="prose prose-invert max-w-none text-gray-400 space-y-6">
        <section>
          <h2 class="text-2xl font-semibold text-white">Introduction</h2>
          <p>
            Our website and mobile app uses cookies. By using our website, mobile app and agreeing to this policy, you consent to our use of cookies, web beacons and similar technologies in accordance with the terms of this policy.
          </p>
        </section>

        <section>
          <h2 class="text-2xl font-semibold text-white">What Are Cookies, Similar Technologies and Web Beacons?</h2>
          <p>
            A "Cookie" is a text file placed on your mobile device internal memory when you visit our website or make use of our mobile app which helps record how you navigate our app or website. Cookies allow our website or mobile app to recognize a particular device or browser and also help us present you tailored options based on the information stored from your previous visit. Cookies do not contain any information that personally identifies you and they don't harm your device in any way.
          </p>
          <p>
            Similar technologies are technologies that are used to store information in your browser or device internal storage, such as HTML 5 cookies, flash cookies, and other web or mobile application methods.
          </p>
          <p>
            Web beacons are small files (also called "pixels", "image tags", or "script tags") that may be loaded on our site or app, that may work in concert with cookies to identify our users and provide anonymized data on their behavior.
          </p>
        </section>

        <section>
          <h2 class="text-2xl font-semibold text-white">Our Use of Cookies, Similar Technologies and Web Beacons</h2>
          <ul class="list-disc pl-6 space-y-2">
            <li><strong class="text-white">Store Preferences and Settings.</strong> Settings that allow our products and services to function correctly or that save your preferences over time may be stored on your device. We also save preferences, such as language, browser and others, so those do not have to be reset each time you return to the site.</li>
            <li><strong class="text-white">Security.</strong> We use cookies to detect fraudulent activities and abuse of our app, websites and services.</li>
            <li><strong class="text-white">Store the Information You Provide.</strong> Your email address, feedbacks and other information you offered when using our Services.</li>
            <li><strong class="text-white">Social Media.</strong> Our website and app may include social media cookies that enable users who are logged in to the social media service to share content via that service.</li>
            <li><strong class="text-white">Performance.</strong> VidGen uses cookies for load balancing to ensure that websites remain up and running.</li>
            <li><strong class="text-white">Analytics.</strong> In order to provide you our products and services, cookies and other identifiers are used to gather usage and performance data. For example, we make use of cookies to determine the number of unique visitors to each web page or services used and to develop other statistics about the operations of our products and services. This includes cookies from VidGen and from third-party analytics providers.</li>
          </ul>
          <p class="mt-4">
            Please note that some third party links on our mobile app and website (including, for example, providers of external services like web traffic analysis services and payment processing) may also use cookies, over which we have no control. These cookies are likely to be performance/analytical cookies or targeted cookies.
          </p>
        </section>

        <section>
          <h2 class="text-2xl font-semibold text-white">Types of Cookies</h2>

          <h3 class="text-xl font-semibold text-white mt-6 mb-2">Session Cookies</h3>
          <p>
            This type of cookie is only stored on your device during a browsing session and are automatically erased from your device once you close our app – they usually store an anonymous session ID allowing you to use our app or browse a website without having to log in to each page but they do not collect any personal data from your device.
          </p>

          <h3 class="text-xl font-semibold text-white mt-6 mb-2">Persistent Cookies</h3>
          <p>
            This type of cookie is stored on your device as a file and remains on your device after a browsing session or when you close our app. The cookie can only be read by the website or app that created it when you visit that website again. [Persistent cookies are used for Google Analytics.]
          </p>

          <p class="mt-6">Cookies can also be classified as follows:</p>

          <h3 class="text-xl font-semibold text-white mt-6 mb-2">Strictly Necessary Cookies</h3>
          <p>
            These are essential cookies to enable you to use our app and website effectively, such as when buying a product and/or service, and therefore cannot be restricted. Without these cookies, our services may not be available to you.
          </p>

          <h3 class="text-xl font-semibold text-white mt-6 mb-2">Performance Cookies</h3>
          <p>
            Such cookies allow us to monitor and improve our app or website performance. For example, they allow us to evaluate number of visits, identify sources of traffic and see which parts of the site are most visited.
          </p>

          <h3 class="text-xl font-semibold text-white mt-6 mb-2">Functionality Cookies</h3>
          <p>
            These cookies allow our website to remember your preferences and provide improved features. For instance, we may be able to provide you with information or updates relevant to the services you use. The type of information collected by these cookies is usually anonymized.
          </p>
        </section>

        <section>
          <h2 class="text-2xl font-semibold text-white">How to Block or Delete Cookies</h2>
          <p>
            You can check or change the type of cookies you accept within your browser setting at any time. You can also restrict all cookies any time through your browser settings. However, if you restrict cookies on your browser or device (including essential cookies) you may not be able to make use of our Services or website.
          </p>
        </section>

        <section>
          <h2 class="text-2xl font-semibold text-white">How to Contact Us</h2>
          <p>
            If you have any questions about this Cookie Policy, please contact us at <a :href="'mailto:' + config.public.companyEmail" class="text-violet-400 hover:text-violet-300">{{ config.public.companyEmail }}</a>.
          </p>
          <p class="mt-4">
            For more information about how we collect and use your personal information, please see our <NuxtLink to="/privacy" class="text-violet-400 hover:text-violet-300">Privacy Policy</NuxtLink>.
          </p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()

useHead({
  title: 'Cookie Policy - VidGen',
  meta: [
    { name: 'description', content: 'Cookie Policy and website data practices for VidGen.' }
  ]
})
</script>
