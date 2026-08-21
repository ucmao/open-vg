/**
 * SEO Meta Tags Plugin
 * Loads and injects global meta tags from backend configuration.
 * Supports SSR for basic TDK and Script injection.
 * Custom code is NOT injected on /admin routes.
 */
export default defineNuxtPlugin(async () => {
  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl as string
  const route = useRoute()

  // Determine the base URL for SSR vs Client
  let baseUrl = apiBaseUrl
  if (process.server && (!baseUrl || baseUrl.startsWith('/'))) {
    baseUrl = process.env.NUXT_PUBLIC_INTERNAL_API_URL || 'http://localhost:8000'
  }

  try {
    // Fetch meta tags configuration from backend
    const { data: result } = await useFetch<any>(`${baseUrl}/api/seo/meta-tags`, {
      key: 'global-seo-meta'
    })

    if (result.value && result.value.success && result.value.data) {
      const metaTags = result.value.data

      // Use a function so useHead reacts to route: do not inject custom code on /admin
      useHead(() => {
        const isAdminRoute = route.path.startsWith('/admin')
        const headConfig: any = {
          meta: [],
          script: [],
          noscript: []
        }

        // 1. Basic TDK
        if (metaTags.site_name) {
          headConfig.titleTemplate = (titleChunk: string) => {
            return titleChunk ? `${titleChunk} - ${metaTags.site_name}` : metaTags.site_name;
          }
        }

        if (metaTags.site_keywords) {
          headConfig.meta.push({ name: 'keywords', content: metaTags.site_keywords })
        }

        // 2. Process all meta tags and custom codes
        Object.keys(metaTags).forEach(key => {
          // Skip basic settings already handled
          if (['site_name', 'site_description', 'site_keywords'].includes(key)) return;

          const content = metaTags[key]?.trim();
          if (!content) return;

          // --- Custom Code: do NOT inject on /admin pages ---
          if (key.startsWith('custom_code_')) {
            if (isAdminRoute) return;
          }

          // --- Google Analytics Special Handling (Legacy) ---
          if (key === 'meta_google_analytics' && (content.startsWith('G-') || content.startsWith('UA-'))) {
            headConfig.script.push({
              src: `https://www.googletagmanager.com/gtag/js?id=${content}`,
              async: true
            });
            headConfig.script.push({
              innerHTML: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', '${content}');
            `
            });
            return;
          }

          // --- Facebook Pixel Special Handling (Legacy) ---
          if (key === 'meta_facebook_pixel' && /^\d+$/.test(content)) {
            headConfig.script.push({
              innerHTML: `
              !function(f,b,e,v,n,t,s)
              {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
              n.callMethod.apply(n,arguments):n.queue.push(arguments)};
              if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
              n.queue=[];t=b.createElement(e);t.async=!0;
              t.src=v;s=b.getElementsByTagName(e)[0];
              s.parentNode.insertBefore(t,s)}(window, document,'script',
              'https://connect.facebook.net/en_US/fbevents.js');
              fbq('init', '${content}');
              fbq('track', 'PageView');
            `
            });
            headConfig.noscript.push({
              innerHTML: `<img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id=${content}&ev=PageView&noscript=1" />`
            });
            return;
          }

          // --- Custom Code Injection (Head or Body) ---
          if (key.startsWith('custom_code_')) {
            const isBody = key.startsWith('custom_code_body_');

            // Match <meta ...>
            const metaMatches = content.matchAll(/<meta\s+([^>]+)>/gi);
            for (const match of metaMatches) {
              const attrStr = match[1];
              const attrs: any = {};
              const attrMatches = attrStr.matchAll(/([a-z-]+)=["']([^"']*)["']/gi);
              for (const aMatch of attrMatches) {
                attrs[aMatch[1].toLowerCase()] = aMatch[2];
              }
              headConfig.meta.push(attrs);
            }

            // Match <script ...>...</script>
            const scriptMatches = content.matchAll(/<script\s*([^>]*)>([\s\S]*?)<\/script>/gi);
            for (const match of scriptMatches) {
              const attrStr = match[1];
              const scriptBody = match[2];
              const scriptObj: any = { innerHTML: scriptBody };

              if (isBody) scriptObj.tagPosition = 'bodyClose';

              const attrMatches = attrStr.matchAll(/([a-z-]+)(?:=["']([^"']*)["'])?/gi);
              for (const aMatch of attrMatches) {
                const name = aMatch[1].toLowerCase();
                const value = aMatch[2] || true;
                scriptObj[name] = value;
              }
              headConfig.script.push(scriptObj);
            }

            // Match <link ...>
            const linkMatches = content.matchAll(/<link\s+([^>]+)>/gi);
            for (const match of linkMatches) {
              const attrStr = match[1];
              const attrs: any = {};
              const attrMatches = attrStr.matchAll(/([a-z-]+)=["']([^"']*)["']/gi);
              for (const aMatch of attrMatches) {
                attrs[aMatch[1].toLowerCase()] = aMatch[2];
              }
              headConfig.link = headConfig.link || [];
              headConfig.link.push(attrs);
            }
          }
        });

        return headConfig
      })
    }
  } catch (error) {
    // console.warn('⚠️ Failed to load SEO meta tags:', error)
  }
})
