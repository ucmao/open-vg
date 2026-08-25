<template>
  <div class="min-h-screen bg-[#0a0a0f] pt-32 pb-20">
    <div class="container mx-auto px-4 max-w-4xl">
      <h1 class="text-4xl font-bold text-white mb-4">Help Center</h1>
      <p class="text-gray-400 mb-12">Find answers to common questions and get help with VidGen</p>
      
      <div class="space-y-8">
        <!-- Getting Started -->
        <section class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-6">
          <h2 class="text-2xl font-semibold text-white mb-4">Getting Started</h2>
          <div class="space-y-4">
            <div>
              <h3 class="text-lg font-medium text-white mb-2">How do I create an account?</h3>
              <p class="text-gray-400">
                Click on "Login" in the top right corner, then select "Register" to create a new account. You can sign up with your email or use Google OAuth for quick registration.
              </p>
            </div>
            <div>
              <h3 class="text-lg font-medium text-white mb-2">How do I generate images or videos?</h3>
              <p class="text-gray-400">
                Navigate to the "Create Art" page, select your generation type (Text to Image, Image to Image, Text to Video, or Image to Video), choose a model, enter your prompt, and click "Generate". Make sure you have sufficient credits.
              </p>
            </div>
            <div>
              <h3 class="text-lg font-medium text-white mb-2">What are credits and how do I get them?</h3>
              <p class="text-gray-400">
                Credits are the currency used to generate content on VidGen. You can purchase credits on the "Pricing" page. Different models have different credit costs - check the model description for pricing details.
              </p>
            </div>
          </div>
        </section>

        <!-- Generation & Models -->
        <section class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-6">
          <h2 class="text-2xl font-semibold text-white mb-4">Generation & Models</h2>
          <div class="space-y-4">
            <div>
              <h3 class="text-lg font-medium text-white mb-2">How long does generation take?</h3>
              <p class="text-gray-400">
                Generation time varies by model and content type. Images typically take 10-30 seconds, while videos can take 1-5 minutes depending on the model and duration.
              </p>
            </div>
            <div>
              <h3 class="text-lg font-medium text-white mb-2">What models are available?</h3>
              <p class="text-gray-400">
                We offer a variety of models for different use cases, including FLUX, Ideogram, Kling, Veo, SeeDance, WAN, and more. Each model has unique strengths - check the model descriptions to find the best fit for your needs.
              </p>
            </div>
            <div>
              <h3 class="text-lg font-medium text-white mb-2">Can I use my generated content commercially?</h3>
              <p class="text-gray-400">
                Yes, you own the rights to all content you generate on VidGen. You can use it for personal or commercial purposes. However, please review the specific model's terms of service for any restrictions.
              </p>
            </div>
          </div>
        </section>

        <!-- Credits & Billing -->
        <section class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-6">
          <h2 class="text-2xl font-semibold text-white mb-4">Credits & Billing</h2>
          <div class="space-y-4">
            <div>
              <h3 class="text-lg font-medium text-white mb-2">How do I purchase credits?</h3>
              <p class="text-gray-400">
                Go to the "Pricing" page and select a credit package. We accept payments through PayPal. After successful payment, credits will be automatically added to your account.
              </p>
            </div>
            <div>
              <h3 class="text-lg font-medium text-white mb-2">Do credits expire?</h3>
              <p class="text-gray-400">
                Credits do not expire. You can use them at any time after purchase.
              </p>
            </div>
            <div>
              <h3 class="text-lg font-medium text-white mb-2">What if my generation fails?</h3>
              <p class="text-gray-400">
                If a generation fails due to a technical error, we automatically refund the credits used. You can check your credit history in the "Billing" section of your profile.
              </p>
            </div>
            <div>
              <h3 class="text-lg font-medium text-white mb-2">Can I get a refund?</h3>
              <p class="text-gray-400">
                Please refer to our <NuxtLink to="/refund" class="text-violet-400 hover:text-violet-300">Refund Policy</NuxtLink> for details on refund eligibility and procedures.
              </p>
            </div>
          </div>
        </section>

        <!-- Account & Profile -->
        <section class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-6">
          <h2 class="text-2xl font-semibold text-white mb-4">Account & Profile</h2>
          <div class="space-y-4">
            <div>
              <h3 class="text-lg font-medium text-white mb-2">How do I change my password?</h3>
              <p class="text-gray-400">
                If you signed up with email, you can reset your password using the "Forgot Password" link on the login page. If you signed up with Google, your password is managed by Google.
              </p>
            </div>
            <div>
              <h3 class="text-lg font-medium text-white mb-2">How do I share my creations?</h3>
              <p class="text-gray-400">
                All your generated content is automatically saved to your profile. You can view and share your creations from your profile page. Each work has a unique URL that you can share.
              </p>
            </div>
            <div>
              <h3 class="text-lg font-medium text-white mb-2">Can I delete my account?</h3>
              <p class="text-gray-400">
                Currently, account deletion is not available through the interface. Please contact us at <a :href="'mailto:' + config.public.companyEmail" class="text-violet-400 hover:text-violet-300">{{ config.public.companyEmail }}</a> if you need to delete your account.
              </p>
            </div>
          </div>
        </section>

        <!-- Technical Support -->
        <section class="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-6">
          <h2 class="text-2xl font-semibold text-white mb-4">Technical Support</h2>
          <div class="space-y-4">
            <div>
              <h3 class="text-lg font-medium text-white mb-2">What browsers are supported?</h3>
              <p class="text-gray-400">
                VidGen works best on modern browsers including Chrome, Firefox, Safari, and Edge. Make sure you're using the latest version for the best experience.
              </p>
            </div>
            <div>
              <h3 class="text-lg font-medium text-white mb-2">I'm experiencing errors. What should I do?</h3>
              <p class="text-gray-400">
                Try refreshing the page or clearing your browser cache. If the issue persists, please contact us with details about the error message and what you were trying to do.
              </p>
            </div>
            <div>
              <h3 class="text-lg font-medium text-white mb-2">How do I contact support?</h3>
              <p class="text-gray-400">
                For technical support or questions, please email us at <a :href="'mailto:' + config.public.companyEmail" class="text-violet-400 hover:text-violet-300">{{ config.public.companyEmail }}</a>. We typically respond within 24-48 hours.
              </p>
            </div>
          </div>
        </section>

        <!-- Contact Section -->
        <section class="bg-gradient-to-br from-violet-500/10 to-pink-500/10 backdrop-blur border border-violet-500/20 rounded-2xl p-8 text-center">
          <h2 class="text-2xl font-semibold text-white mb-4">Still Need Help?</h2>
          <p class="text-gray-400 mb-6">
            Can't find what you're looking for? We're here to help!
          </p>
          <div class="space-y-3">
            <a :href="'mailto:' + config.public.companyEmail" class="inline-block px-6 py-3 bg-violet-600 hover:bg-violet-700 text-white font-semibold rounded-xl transition-colors">
              Contact Support
            </a>
            <p class="text-sm text-gray-500 mt-4">
              Email: <a :href="'mailto:' + config.public.companyEmail" class="text-violet-400 hover:text-violet-300">{{ config.public.companyEmail }}</a>
            </p>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()

useHead({
  title: 'Help Center — VidGen',
  meta: [
    { name: 'description', content: 'Get help with VidGen - Find answers to common questions about account, credits, generation, and more.' }
  ]
})
</script>
