<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- Sidebar Overlay (Mobile) -->
    <div 
      v-if="isSidebarOpen" 
      class="fixed inset-0 z-40 bg-gray-900/50 backdrop-blur-sm md:hidden"
      @click="isSidebarOpen = false"
    ></div>

    <!-- Sidebar: full on mobile (translate), desktop expanded w-52 / collapsed w-16 -->
    <aside 
      class="fixed left-0 top-0 h-full bg-white border-r border-gray-200 flex flex-col z-50 transition-all duration-300 w-52 md:shrink-0"
      :class="[
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full',
        'md:translate-x-0',
        sidebarCollapsed ? 'md:w-16' : 'md:w-52'
      ]"
    >
      <!-- Logo / Collapse toggle -->
      <div 
        class="h-16 px-4 flex items-center justify-between border-b border-gray-200 shrink-0 min-w-0 transition-[padding] duration-300"
        :class="sidebarCollapsed ? 'md:justify-center md:px-0' : ''"
      >
        <NuxtLink 
          to="/workspace/dashboard" 
          class="flex items-center gap-2 min-w-0 overflow-hidden"
          :class="sidebarCollapsed ? 'md:w-0 md:opacity-0 md:pointer-events-none md:overflow-hidden md:invisible' : ''"
        >
          <img src="/vidgen-logo.png" alt="VidGen Logo" class="h-7 w-auto object-contain shrink-0" />
        </NuxtLink>
        <div class="flex items-center shrink-0 gap-1" :class="sidebarCollapsed ? 'md:absolute md:left-1/2 md:-translate-x-1/2' : ''">
          <!-- Desktop: collapse / expand -->
          <button 
            v-if="!isMobile"
            @click="toggleSidebarCollapsed"
            class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            :title="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
          >
            <ChevronsLeft 
              class="w-5 h-5 transition-transform duration-200" 
              :class="{ 'rotate-180': sidebarCollapsed }"
            />
          </button>
          <!-- Mobile Close Button -->
          <button 
            @click="isSidebarOpen = false"
            class="p-2 -mr-2 text-gray-400 hover:text-gray-600 md:hidden"
          >
            <X class="w-6 h-6" />
          </button>
        </div>
      </div>

      <!-- Collapsed: only group icons -->
      <nav 
        v-show="sidebarCollapsed && !isMobile" 
        class="flex-1 flex flex-col items-center py-3 gap-1 overflow-y-auto"
      >
        <button type="button" @click="expandSidebarAndGroup('workspace')" class="w-10 h-10 flex items-center justify-center rounded-lg transition-colors" :class="isGroupActive('workspace') ? 'bg-blue-50 text-blue-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'" title="Workspace">
          <Home class="w-5 h-5" />
        </button>
        <button type="button" @click="expandSidebarAndGroup('userCenter')" class="w-10 h-10 flex items-center justify-center rounded-lg transition-colors" :class="isGroupActive('userCenter') ? 'bg-blue-50 text-blue-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'" title="Users">
          <Users class="w-5 h-5" />
        </button>
        <button type="button" @click="expandSidebarAndGroup('moderation')" class="w-10 h-10 flex items-center justify-center rounded-lg transition-colors" :class="isGroupActive('moderation') ? 'bg-blue-50 text-blue-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'" title="Moderation">
          <ShieldAlert class="w-5 h-5" />
        </button>
        <button type="button" @click="expandSidebarAndGroup('content')" class="w-10 h-10 flex items-center justify-center rounded-lg transition-colors" :class="isGroupActive('content') ? 'bg-blue-50 text-blue-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'" title="Content">
          <BookOpen class="w-5 h-5" />
        </button>
        <button type="button" @click="expandSidebarAndGroup('modelDriven')" class="w-10 h-10 flex items-center justify-center rounded-lg transition-colors" :class="isGroupActive('modelDriven') ? 'bg-blue-50 text-blue-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'" title="Models">
          <Lightbulb class="w-5 h-5" />
        </button>
        <button type="button" @click="expandSidebarAndGroup('assets')" class="w-10 h-10 flex items-center justify-center rounded-lg transition-colors" :class="isGroupActive('assets') ? 'bg-blue-50 text-blue-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'" title="Finance">
          <CircleDollarSign class="w-5 h-5" />
        </button>
        <button type="button" @click="expandSidebarAndGroup('system')" class="w-10 h-10 flex items-center justify-center rounded-lg transition-colors" :class="isGroupActive('system') ? 'bg-blue-50 text-blue-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'" title="Pages">
          <Settings class="w-5 h-5" />
        </button>
        <button type="button" @click="expandSidebarAndGroup('website')" class="w-10 h-10 flex items-center justify-center rounded-lg transition-colors" :class="isGroupActive('website') ? 'bg-blue-50 text-blue-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'" title="Site">
          <Globe class="w-5 h-5" />
        </button>
      </nav>

      <!-- Expanded: full navigation -->
      <nav 
        v-show="!sidebarCollapsed || isMobile" 
        class="flex-1 px-3 py-4 space-y-2 overflow-y-auto"
      >
        <!-- Workspace -->
        <div class="nav-group">
          <button
            @click="toggleGroup('workspace')"
            class="w-full flex items-center justify-between px-3 py-3 text-sm font-medium rounded-lg transition-colors"
            :class="isGroupActive('workspace') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'"
          >
            <span class="flex items-center gap-2">
              <Home class="w-4 h-4 shrink-0" />
              {{ t('nav.workspace', 'Workspace') }}
            </span>
            <ChevronDown
              class="w-4 h-4 transition-transform duration-200 shrink-0"
              :class="{ 'rotate-180': expandedGroups.workspace }"
            />
          </button>
          <div v-show="expandedGroups.workspace" class="space-y-0.5 mt-1 pl-5">
            <NuxtLink
              to="/workspace/dashboard"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/workspace/dashboard')"
            >
              <LayoutDashboard class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.dashboard', 'Dashboard') }}
            </NuxtLink>
            <NuxtLink
              to="/workspace/analytics"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/workspace/analytics')"
            >
              <BarChart3 class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.analytics', 'Analytics') }}
            </NuxtLink>
          </div>
        </div>

        <!-- User Management -->
        <div class="nav-group">
          <button
            @click="toggleGroup('userCenter')"
            class="w-full flex items-center justify-between px-3 py-3 text-sm font-medium rounded-lg transition-colors"
            :class="isGroupActive('userCenter') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'"
          >
            <span class="flex items-center gap-2">
              <Users class="w-4 h-4 shrink-0" />
              {{ t('nav.user_management', 'User Management') }}
            </span>
            <ChevronDown
              class="w-4 h-4 transition-transform duration-200 shrink-0"
              :class="{ 'rotate-180': expandedGroups.userCenter }"
            />
          </button>
          <div v-show="expandedGroups.userCenter" class="space-y-0.5 mt-1 pl-5">
            <NuxtLink
              to="/users/list"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/users/list')"
            >
              <UserCircle class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.user_list', 'User List') }}
            </NuxtLink>
            <NuxtLink
              to="/users/works"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/users/works')"
            >
              <Image class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.works_list', 'Works Management') }}
            </NuxtLink>
            <NuxtLink
              to="/users/comments"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/users/comments')"
            >
              <MessageSquare class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.comments', 'Comments') }}
            </NuxtLink>
            <NuxtLink
              to="/users/sockpuppets"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/users/sockpuppets')"
            >
              <UsersRound class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.sockpuppets', 'Sockpuppets') }}
            </NuxtLink>
          </div>
        </div>

        <!-- Content Moderation -->
        <div class="nav-group">
          <button
            @click="toggleGroup('moderation')"
            class="w-full flex items-center justify-between px-3 py-3 text-sm font-medium rounded-lg transition-colors"
            :class="isGroupActive('moderation') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'"
          >
            <span class="flex items-center gap-2">
              <ShieldAlert class="w-4 h-4 shrink-0" />
              {{ t('nav.moderation', 'Content Moderation') }}
            </span>
            <ChevronDown
              class="w-4 h-4 transition-transform duration-200 shrink-0"
              :class="{ 'rotate-180': expandedGroups.moderation }"
            />
          </button>
          <div v-show="expandedGroups.moderation" class="space-y-0.5 mt-1 pl-5">
            <NuxtLink
              to="/moderation/reports"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/moderation/reports')"
            >
              <Flag class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.reports', 'Reports') }}
            </NuxtLink>
            <NuxtLink
              to="/moderation/nsfw"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/moderation/nsfw')"
            >
              <TriangleAlert class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.nsfw', 'NSFW Moderation') }}
            </NuxtLink>
            <NuxtLink
              to="/moderation/lexicons"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/moderation/lexicons')"
            >
              <BookMarked class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.lexicon', 'Sensitive Lexicon') }}
            </NuxtLink>
            <NuxtLink
              to="/moderation/hidden"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/moderation/hidden')"
            >
              <EyeOff class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.hidden_config', 'Hidden Config') }}
            </NuxtLink>
          </div>
        </div>

        <!-- Operations & Content -->
        <div class="nav-group">
          <button
            @click="toggleGroup('content')"
            class="w-full flex items-center justify-between px-3 py-3 text-sm font-medium rounded-lg transition-colors"
            :class="isGroupActive('content') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'"
          >
            <span class="flex items-center gap-2">
              <BookOpen class="w-4 h-4 shrink-0" />
              {{ t('nav.content_management', 'Content Operations') }}
            </span>
            <ChevronDown
              class="w-4 h-4 transition-transform duration-200 shrink-0"
              :class="{ 'rotate-180': expandedGroups.content }"
            />
          </button>
          <div v-show="expandedGroups.content" class="space-y-0.5 mt-1 pl-5">
            <NuxtLink
              to="/content/blog"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/content/blog', false)"
            >
              <FileText class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.blog', 'Blog Posts') }}
            </NuxtLink>
            <NuxtLink
              to="/content/topics"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/content/topics')"
            >
              <LayoutGrid class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.topics', 'Topics & Specials') }}
            </NuxtLink>
            <NuxtLink
              to="/content/taxonomy"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/content/taxonomy')"
            >
              <Tags class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.taxonomy', 'Taxonomy & Tags') }}
            </NuxtLink>
            <NuxtLink
              to="/content/media"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/content/media')"
            >
              <Package class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.media', 'Media Assets') }}
            </NuxtLink>
          </div>
        </div>

        <!-- Models & Workflows -->
        <div class="nav-group">
          <button
            @click="toggleGroup('modelDriven')"
            class="w-full flex items-center justify-between px-3 py-3 text-sm font-medium rounded-lg transition-colors"
            :class="isGroupActive('modelDriven') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'"
          >
            <span class="flex items-center gap-2">
              <Lightbulb class="w-4 h-4 shrink-0" />
              {{ t('nav.model_management', 'Model Management') }}
            </span>
            <ChevronDown
              class="w-4 h-4 transition-transform duration-200 shrink-0"
              :class="{ 'rotate-180': expandedGroups.modelDriven }"
            />
          </button>
          <div v-show="expandedGroups.modelDriven" class="space-y-0.5 mt-1 pl-5">
            <NuxtLink
              to="/models/pricing"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/models/pricing')"
            >
              <BadgeDollarSign class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.pricing', 'Model Pricing') }}
            </NuxtLink>
            <NuxtLink
              to="/models/list"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/models/list')"
              @click="isSidebarOpen = false"
            >
              <Cpu class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.models_list', 'Models List') }}
            </NuxtLink>
            <NuxtLink
              to="/models/workflows"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/models/workflows', false)"
            >
              <Workflow class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.workflows', 'Workflows') }}
            </NuxtLink>
            <NuxtLink
              to="/models/api-config"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/models/api-config')"
            >
              <Code class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.api_library', 'API Providers') }}
            </NuxtLink>
          </div>
        </div>

        <!-- Finance -->
        <div class="nav-group">
          <button
            @click="toggleGroup('assets')"
            class="w-full flex items-center justify-between px-3 py-3 text-sm font-medium rounded-lg transition-colors"
            :class="isGroupActive('assets') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'"
          >
            <span class="flex items-center gap-2">
              <CircleDollarSign class="w-4 h-4 shrink-0" />
              {{ t('nav.finance', 'Finance & Billing') }}
            </span>
            <ChevronDown
              class="w-4 h-4 transition-transform duration-200 shrink-0"
              :class="{ 'rotate-180': expandedGroups.assets }"
            />
          </button>
          <div v-show="expandedGroups.assets" class="space-y-0.5 mt-1 pl-5">
            <NuxtLink
              to="/finance/recharge-discount"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/finance/recharge-discount')"
            >
              <Percent class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.discounts', 'Discounts & Offers') }}
            </NuxtLink>
            <NuxtLink
              to="/finance/recharges"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/finance/recharges')"
            >
              <CreditCard class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.recharges', 'Recharge Records') }}
            </NuxtLink>
            <NuxtLink
              to="/finance/credits"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/finance/credits')"
            >
              <TrendingUp class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.credits_log', 'Credits Log') }}
            </NuxtLink>
            <NuxtLink
              to="/finance/packages"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/finance/packages')"
            >
              <ShoppingBag class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.packages', 'Packages') }}
            </NuxtLink>
          </div>
        </div>

        <!-- Page Management -->
        <div class="nav-group">
          <button
            @click="toggleGroup('system')"
            class="w-full flex items-center justify-between px-3 py-3 text-sm font-medium rounded-lg transition-colors"
            :class="isGroupActive('system') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'"
          >
            <span class="flex items-center gap-2">
              <Settings class="w-4 h-4 shrink-0" />
              {{ t('nav.page_management', 'Page Management') }}
            </span>
            <ChevronDown
              class="w-4 h-4 transition-transform duration-200 shrink-0"
              :class="{ 'rotate-180': expandedGroups.system }"
            />
          </button>
          <div v-show="expandedGroups.system" class="space-y-0.5 mt-1 pl-5">
            <NuxtLink
              to="/system/page-seo"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/system/page-seo')"
            >
              <Search class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.primary_pages', 'Primary Pages') }}
            </NuxtLink>
            <NuxtLink
              to="/system/category-pages"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/system/category-pages')"
            >
              <Layers class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.category_pages', 'Category Pages') }}
            </NuxtLink>
            <NuxtLink
              to="/system/effects-pages"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/system/effects-pages')"
            >
              <Zap class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.effects_pages', 'Effects Pages') }}
            </NuxtLink>
            <NuxtLink
              to="/system/generate-pages"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/system/generate-pages')"
            >
              <Wand2 class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.generate_pages', 'Generate Pages') }}
            </NuxtLink>
            <NuxtLink
              to="/system/prompt-settings"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/system/prompt-settings')"
            >
              <ScrollText class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.prompt_settings', 'Work Detail Pages') }}
            </NuxtLink>
          </div>
        </div>

        <!-- Site Settings -->
        <div class="nav-group">
          <button
            @click="toggleGroup('website')"
            class="w-full flex items-center justify-between px-3 py-3 text-sm font-medium rounded-lg transition-colors"
            :class="isGroupActive('website') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'"
          >
            <span class="flex items-center gap-2">
              <Globe class="w-4 h-4 shrink-0" />
              {{ t('nav.site_management', 'Site Settings') }}
            </span>
            <ChevronDown
              class="w-4 h-4 transition-transform duration-200 shrink-0"
              :class="{ 'rotate-180': expandedGroups.website }"
            />
          </button>
          <div v-show="expandedGroups.website" class="space-y-0.5 mt-1 pl-5">
            <NuxtLink
              to="/system/homepage-management"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/system/homepage-management')"
            >
              <Sparkles class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.homepage', 'Homepage Activity') }}
            </NuxtLink>
            <NuxtLink
              to="/system/website-settings"
              class="flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors"
              :class="isActive('/system/website-settings')"
            >
              <SlidersHorizontal class="w-4 h-4 mr-2.5 shrink-0" />
              {{ t('nav.general_settings', 'General Settings') }}
            </NuxtLink>
          </div>
        </div>
      </nav>

      <!-- User Menu -->
      <div 
        class="p-4 border-t border-gray-200 transition-[padding] duration-300"
        :class="sidebarCollapsed ? 'md:py-3 md:px-2' : ''"
      >
        <div 
          class="flex items-center justify-between"
          :class="sidebarCollapsed ? 'md:justify-center' : ''"
        >
          <div class="flex items-center space-x-3" :class="sidebarCollapsed ? 'md:space-x-0' : ''">
            <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
              <span class="text-sm font-semibold text-blue-700">A</span>
            </div>
            <div class="flex-1 min-w-0" :class="sidebarCollapsed ? 'md:w-0 md:overflow-hidden md:opacity-0' : ''">
              <p class="text-sm font-medium text-gray-900 truncate">{{ t('role.admin', 'Administrator') }}</p>
            </div>
          </div>
          <button
            @click="handleLogout"
            class="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors shrink-0"
            :class="sidebarCollapsed ? 'md:w-0 md:opacity-0 md:pointer-events-none md:p-0 md:overflow-hidden' : ''"
            :title="t('action.logout', 'Sign Out')"
          >
            <LogOut class="w-5 h-5" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div 
      class="flex-1 flex flex-col min-w-0 transition-[padding] duration-300"
      :class="sidebarCollapsed ? 'md:pl-16' : 'md:pl-52'"
    >
      <!-- Top Bar -->
      <header class="sticky top-0 z-40 h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 sm:px-6">
        <div class="flex items-center space-x-3">
          <!-- Mobile Menu Toggle -->
          <button 
            @click="isSidebarOpen = true"
            class="p-2 -ml-2 text-gray-500 hover:text-gray-600 md:hidden"
          >
            <Menu class="w-6 h-6" />
          </button>
          <!-- Desktop: Expand sidebar when collapsed -->
          <button 
            v-if="!isMobile && sidebarCollapsed"
            @click="sidebarCollapsed = false"
            class="p-2 -ml-2 text-gray-500 hover:text-gray-600 hover:bg-gray-100 rounded-lg hidden md:flex"
            title="Expand sidebar"
          >
            <Menu class="w-6 h-6" />
          </button>
          <h1 class="text-lg font-semibold text-gray-900 truncate">{{ pageTitle }}</h1>
        </div>

        <!-- Language Switcher in Header -->
        <div class="flex items-center space-x-3">
          <select
            :value="lang"
            @change="(e: any) => setLanguage(e.target.value)"
            class="text-xs border rounded-lg px-2.5 py-1.5 bg-white text-gray-700 outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer shadow-sm font-medium"
          >
            <option value="en">🇬🇧 English</option>
            <option value="zh">🇨🇳 简体中文</option>
            <option value="ja">🇯🇵 日本語</option>
            <option value="ko">🇰🇷 한국어</option>
            <option value="es">🇪🇸 Español</option>
            <option value="pt">🇧🇷 Português</option>
            <option value="de">🇩🇪 Deutsch</option>
            <option value="fr">🇫🇷 Français</option>
          </select>
        </div>
      </header>

      <!-- Page Content -->
      <main class="p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive, watch, onMounted, onUnmounted } from 'vue'
import {
  ChevronDown,
  ChevronsLeft,
  X,
  Menu,
  Home,
  LayoutDashboard,
  BarChart3,
  Users,
  UserCircle,
  Image,
  MessageSquare,
  UsersRound,
  ShieldAlert,
  Flag,
  TriangleAlert,
  BookMarked,
  EyeOff,
  BookOpen,
  FileText,
  LayoutGrid,
  Tags,
  Package,
  Lightbulb,
  Cpu,
  CircleDollarSign,
  Workflow,
  Code,
  Percent,
  Settings,
  Search,
  Globe,
  Zap,
  LogOut,
  Sparkles,
  CreditCard,
  TrendingUp,
  Layers,
  ShoppingBag,
  ScrollText,
  BadgeDollarSign,
  SlidersHorizontal,
  Wand2,
} from '@lucide/vue'

const route = useRoute()
const router = useRouter()
const { logout } = useAdminAuth()
const { lang, setLanguage, t } = useAdminI18n()

const isSidebarOpen = ref(false)

// Desktop sidebar collapsed state
const SIDEBAR_COLLAPSED_KEY = 'admin_sidebar_collapsed'
const sidebarCollapsed = ref(false)

// Navigation group expansion state
const EXPANDED_GROUPS_KEY = 'admin_sidebar_expanded_groups'
const hasCustomExpandedState = ref(false)

const isMobile = ref(false)
function checkMobile() {
  isMobile.value = typeof window !== 'undefined' && window.innerWidth < 768
}

const expandedGroups = reactive({
  workspace: false,
  userCenter: false,
  moderation: false,
  content: false,
  modelDriven: false,
  assets: false,
  website: false,
  system: false
})

function resetExpandedGroups() {
  (Object.keys(expandedGroups) as Array<keyof typeof expandedGroups>).forEach((key) => {
    expandedGroups[key] = false
  })
}

function applyDefaultGroupsByPath(path: string) {
  resetExpandedGroups()
  if (path.startsWith('/workspace')) {
    expandedGroups.workspace = true
  } else if (path.startsWith('/users')) {
    expandedGroups.userCenter = true
  } else if (path.startsWith('/moderation')) {
    expandedGroups.moderation = true
  } else if (path.startsWith('/content')) {
    expandedGroups.content = true
  } else if (path.startsWith('/models')) {
    expandedGroups.modelDriven = true
  } else if (path.startsWith('/finance')) {
    expandedGroups.assets = true
  } else if (path === '/system/homepage-management' || path === '/system/website-settings') {
    expandedGroups.website = true
  } else if (path.startsWith('/system')) {
    expandedGroups.system = true
  } else {
    expandedGroups.workspace = true
  }
}

function saveExpandedGroups() {
  if (!import.meta.client) return
  const payload: Record<string, boolean> = {}
  ;(Object.keys(expandedGroups) as Array<keyof typeof expandedGroups>).forEach((key) => {
    payload[key] = expandedGroups[key]
  })
  localStorage.setItem(EXPANDED_GROUPS_KEY, JSON.stringify(payload))
}

onMounted(() => {
  if (import.meta.client) {
    const storedCollapsed = localStorage.getItem(SIDEBAR_COLLAPSED_KEY)
    if (storedCollapsed !== null) {
      sidebarCollapsed.value = storedCollapsed === 'true'
    }

    const storedGroups = localStorage.getItem(EXPANDED_GROUPS_KEY)
    if (storedGroups) {
      try {
        const parsed = JSON.parse(storedGroups) as Partial<Record<keyof typeof expandedGroups, boolean>>
        let hasAnyExpanded = false
        ;(Object.keys(expandedGroups) as Array<keyof typeof expandedGroups>).forEach((key) => {
          const value = parsed[key]
          if (typeof value === 'boolean') {
            expandedGroups[key] = value
            if (value) hasAnyExpanded = true
          } else {
            expandedGroups[key] = false
          }
        })
        hasCustomExpandedState.value = hasAnyExpanded
      } catch {
        applyDefaultGroupsByPath(route.path)
      }
    } else {
      applyDefaultGroupsByPath(route.path)
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
  }
})

onUnmounted(() => {
  if (import.meta.client) window.removeEventListener('resize', checkMobile)
})

function toggleSidebarCollapsed() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  if (import.meta.client) {
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(sidebarCollapsed.value))
  }
}

const toggleGroup = (groupName: keyof typeof expandedGroups) => {
  expandedGroups[groupName] = !expandedGroups[groupName]
  hasCustomExpandedState.value = true
  saveExpandedGroups()
}

function expandSidebarAndGroup(groupKey: keyof typeof expandedGroups) {
  sidebarCollapsed.value = false
  if (import.meta.client) {
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, 'false')
  }
  resetExpandedGroups()
  expandedGroups[groupKey] = true
  hasCustomExpandedState.value = true
  saveExpandedGroups()

  let targetPath: string | null = null
  switch (groupKey) {
    case 'workspace':
      targetPath = '/workspace/dashboard'
      break
    case 'userCenter':
      targetPath = '/users/list'
      break
    case 'moderation':
      targetPath = '/moderation/reports'
      break
    case 'content':
      targetPath = '/content/blog'
      break
    case 'modelDriven':
      targetPath = '/models/list'
      break
    case 'assets':
      targetPath = '/finance/recharges'
      break
    case 'website':
      targetPath = '/system/homepage-management'
      break
    case 'system':
      targetPath = '/system/page-seo'
      break
  }

  if (targetPath && route.path !== targetPath) {
    router.push(targetPath)
  }
}

function isGroupActive(groupKey: string): boolean {
  const path = route.path
  switch (groupKey) {
    case 'workspace':
      return path.startsWith('/workspace')
    case 'userCenter':
      return path.startsWith('/users')
    case 'moderation':
      return path.startsWith('/moderation')
    case 'content':
      return path.startsWith('/content')
    case 'modelDriven':
      return path.startsWith('/models')
    case 'assets':
      return path.startsWith('/finance')
    case 'website':
      return path === '/system/homepage-management' || path === '/system/website-settings'
    case 'system':
      return path.startsWith('/system') && path !== '/system/homepage-management' && path !== '/system/website-settings'
    default:
      return false
  }
}

const isActive = (path: string, exact: boolean = true) => {
  if (exact) {
    return route.path === path
      ? 'bg-blue-50 text-blue-700'
      : 'text-gray-700 hover:bg-gray-50'
  } else {
    if (path === '/blog' && route.path === '/blog/taxonomy') {
      return 'text-gray-700 hover:bg-gray-50'
    }
    return route.path.startsWith(path)
      ? 'bg-blue-50 text-blue-700'
      : 'text-gray-700 hover:bg-gray-50'
  }
}

watch(() => route.path, (newPath) => {
  isSidebarOpen.value = false

  if (!hasCustomExpandedState.value) {
    applyDefaultGroupsByPath(newPath)
  }
})

const pageTitle = computed(() => {
  if (route.path === '/workspace/dashboard') return t('nav.dashboard', 'Dashboard')
  if (route.path === '/workspace/analytics') return t('nav.analytics', 'Analytics')
  if (route.path === '/users/list') return t('nav.user_list', 'User List')
  if (route.path === '/users/works') return t('nav.works_list', 'Works Management')
  if (route.path === '/users/comments') return t('nav.comments', 'Comments Management')
  if (route.path === '/users/sockpuppets') return t('nav.sockpuppets', 'Sockpuppets Zone')
  if (route.path === '/moderation/reports') return t('nav.reports', 'Reports Management')
  if (route.path === '/moderation/nsfw') return t('nav.nsfw', 'NSFW Moderation')
  if (route.path === '/moderation/logs') return t('nav.nsfw_logs', 'NSFW Audit Logs')
  if (route.path === '/moderation/lexicons') return t('nav.lexicon', 'Sensitive Lexicon')
  if (route.path === '/moderation/hidden') return t('nav.hidden_config', 'Hidden Config')
  if (route.path === '/content/blog') return t('nav.blog', 'Blog Posts')
  if (route.path === '/content/taxonomy') return t('nav.taxonomy', 'Taxonomy & Tags')
  if (route.path.startsWith('/content/blog/new')) return t('nav.new_post', 'New Post')
  if (route.path.includes('/edit')) return t('nav.edit_post', 'Edit Post')
  if (route.path.startsWith('/content/topics')) return t('nav.topics', 'Topics & Specials')
  if (route.path === '/models/list') return t('nav.models_list', 'Models List')
  if (route.path === '/models/pricing') return t('nav.pricing', 'Model Pricing')
  if (route.path === '/models/api-config') return t('nav.api_library', 'API Providers')
  if (route.path.startsWith('/models/workflows')) {
    if (route.params.id === 'new') return t('nav.new_workflow', 'New Workflow')
    if (route.params.id) return t('nav.edit_workflow', 'Edit Workflow')
    return t('nav.workflows', 'Workflows')
  }
  if (route.path === '/finance/recharge-discount') return t('nav.discounts', 'Discounts & Offers')
  if (route.path === '/finance/recharges') return t('nav.recharges', 'Recharge Records')
  if (route.path === '/finance/credits') return t('nav.credits_log', 'Credits Log')
  if (route.path === '/finance/packages') return t('nav.packages', 'Packages Config')
  if (route.path.startsWith('/content/media')) return t('nav.media', 'Media Assets')
  if (route.path === '/system/website-settings') return t('nav.general_settings', 'General Settings')
  if (route.path === '/system/page-seo') return t('nav.primary_pages', 'Primary Pages')
  if (route.path === '/system/category-pages') return t('nav.category_pages', 'Category Pages')
  if (route.path === '/system/effects-pages') return t('nav.effects_pages', 'Effects Pages')
  if (route.path === '/system/generate-pages') return t('nav.generate_pages', 'Generate Pages')
  if (route.path === '/system/prompt-settings') return t('nav.prompt_settings', 'Work Detail Pages')
  if (route.path === '/system/homepage-management') return t('nav.homepage', 'Homepage Activity')
  return t('nav.admin_panel', 'VidGen Admin')
})

const handleLogout = () => {
  logout()
}
</script>
