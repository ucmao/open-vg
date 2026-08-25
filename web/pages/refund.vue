<template>
  <div class="min-h-screen bg-[#0a0a0f] pt-32 pb-20">
    <div class="container mx-auto px-4 max-w-4xl">
      <h1 class="text-4xl font-bold text-white mb-8">Refund Policy</h1>
      <p class="text-gray-500 mb-8">Updated Date: Dec. 3rd, 2025</p>

      <div class="prose prose-invert max-w-none text-gray-400 space-y-6">
        <section>
          <h2 class="text-2xl font-semibold text-white">Subscription Refund Conditions</h2>
          <p>
            Customer satisfaction is always the top priority for VidGen. We work hard to provide our customers with an enjoyable experience for both our software and service.
          </p>
          <p>
            If you have any questions with our software or service, please contact our <a :href="'mailto:' + config.public.companyEmail" class="text-violet-400 hover:text-violet-300">support team</a>. We would like to offer a satisfactory solution to you and keep improving ourselves.
          </p>
        </section>

        <section>
          <h2 class="text-2xl font-semibold text-white">Requesting a Refund</h2>
          <p>
            If you want to cancel your order, please go to the <NuxtLink to="/refund" class="text-violet-400 hover:text-violet-300">Refund Page</NuxtLink> and enter your order number, confirm your order information, then click Refund and submit the Refund Request Form (provide the following information):
          </p>
          <p class="mt-4">To complete the form, you will need the:</p>
          <ul class="list-disc pl-6 space-y-2">
            <li>Reason for requesting a refund.</li>
            <li>Computer Operating System.</li>
            <li>Email address used when making the purchase.</li>
            <li>Order reference number.</li>
            <li>Product name.</li>
          </ul>
          <p class="mt-4">
            We will deal with the refund request within 24 hours on business days based on the terms set out below.
          </p>
        </section>

        <section>
          <h2 class="text-2xl font-semibold text-white">Money Back Guarantee</h2>
          <p>
            VidGen offers a free trial version so that you may test the service for yourself before deciding to purchase. These trial versions allow the users to test the software for flaws, and to ensure that it is working correctly on your device, so you can decide if the service is what you need or not before placing an order.
          </p>
          <p>
            VidGen provides a 30-day Money Back Guarantee. We cannot cancel the order after this period has expired because this is a 'try-before-you-buy' system. Refunds will only be given under this guarantee in the following circumstances:
          </p>
        </section>

        <section>
          <h2 class="text-2xl font-semibold text-white">Accepted Circumstances</h2>
          <p>
            VidGen offers refunds in the following circumstances within 30 days of the date of purchase. The refund will be made to the original account that you used to make the payment.
          </p>
          <ul class="list-disc pl-6 space-y-2">
            <li>If you paid twice or more for one product due to technical problems with the payment platform or other technical reasons. In this case, VidGen will only charge once for one product and will refund the additional payments.</li>
            <li>If you do not receive order information within 24 hours after purchase and haven't received a timely response (within 48 hours) from the VidGen support team after contacting the support center. In this case, VidGen may cancel the order and offer a refund if you request.</li>
            <li>If you have purchased the same product twice or purchase two products with similar functions. VidGen will refund the purchase price of one of the products or exchange one product for you.</li>
            <li>If you didn't know the order was auto-renewable and you never received the auto-renew upcoming notification in your email, you have a case for a refund. Contact us within seven days of the credit card charge, and we'll process your return.</li>
            <li>In the event that the software or service purchased has terminal technical problems, and no solution was provided within 30 days. In such case, VidGen will refund the product price if you are unwilling to wait for an update.</li>
          </ul>
          <p class="mt-4">
            Once we issue a refund, the corresponding license or access will be deactivated, and you are required to cease use of the service and any downloaded software or content as applicable.
          </p>
        </section>

        <section>
          <h2 class="text-2xl font-semibold text-white">Circumstances of No Refund</h2>
          <p>
            We cannot offer a refund in the following circumstances. Depending on these circumstances, we may exchange the product or service for you if you don't need the one you've purchased.
          </p>
          <ul class="list-disc pl-6 space-y-2">
            <li>Failure to supply a reason for requesting a refund.</li>
            <li>If you refuse to cooperate with our support team, you will not receive a refund.</li>
            <li>A refund request due to the failure to receive order information within two hours after placing a successful order. VidGen's system will automatically send a registration email as soon as the payment has been received. However, due to internet or system failures, email spam settings, email typo, etc., there might be some delay. In this case, you can retrieve the order information on your account or contact our support center.</li>
            <li>A refund request due to misunderstanding or lack of understanding of the product's functions and capabilities because you failed to read the product description carefully before purchasing.</li>
            <li>A refund request due to credit card fraud or unauthorized payment. VidGen cooperates with third-party payment processing services, so we are not able to monitor authorization during payment. Please contact your card issuer to resolve the matter.</li>
            <li>A refund request due to your mistake and the problem is not product-related. For example, purchase of an incorrect program, downloading an incorrect version, not enough available disk storage on your computer; you change your mind after the purchase, etc.</li>
            <li>Repeatedly and intentionally purchased similar products.</li>
            <li>Purchased the product on special terms during a sales promotion.</li>
            <li>Purchased similar products from other suppliers.</li>
            <li>Differences in price between different sellers or regions.</li>
          </ul>
          <p class="mt-4">
            We are always open to receive any suggestion or feedback at any time and will make every effort to seek the best way to resolve any problems you may have with VidGen software and service.
          </p>
        </section>

        <section>
          <h2 class="text-2xl font-semibold text-white">How to Contact Us</h2>
          <p>
            For refund requests or any questions about this Refund Policy, please contact us at <a :href="'mailto:' + config.public.companyEmail" class="text-violet-400 hover:text-violet-300">{{ config.public.companyEmail }}</a>.
          </p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()

useHead({
  title: 'Refund Policy - VidGen',
  meta: [
    { name: 'description', content: 'Refund Policy for VidGen.' }
  ]
})
</script>
