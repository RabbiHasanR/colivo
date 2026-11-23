import type { TOC } from '@ember/component/template-only';

interface AuthLayoutSignature {
  Blocks: { default: [] };
}

/**
 * The page frame of log-in and "Choose a home" (colivo-design/web/WebAuth.html):
 * the green "About Colivo" panel beside the content on a wide screen, above
 * it on a phone. The content sits in one 440px column.
 */
const AuthLayout: TOC<AuthLayoutSignature> = <template>
  <div class="flex min-h-screen flex-wrap items-stretch">
    <section
      aria-label="About Colivo"
      class="flex flex-[1_1_420px] flex-col justify-between gap-7 bg-primary p-[clamp(28px,5vw,64px)] text-white"
    >
      <span class="font-display text-xl font-bold">Colivo</span>
      <div class="flex max-w-[520px] flex-col gap-4">
        <h1
          class="text-[clamp(30px,3.4vw,46px)] leading-[1.1] font-semibold"
        >Meals, groceries, rent and bills for your shared home. No spreadsheet.</h1>
        <p class="text-base leading-relaxed opacity-90">Everyone logs their own
          meals, uploads receipts and sees what they owe. The month closes with
          one tap.</p>
      </div>
      <ul class="flex flex-wrap gap-x-[22px] gap-y-2.5 text-sm opacity-90">
        <li>✓ Cost per meal, worked out live</li>
        <li>✓ Grocery fund and bills</li>
        <li>✓ Deposits and notice periods</li>
      </ul>
    </section>

    <main
      class="flex flex-[1_1_480px] items-center justify-center px-4 py-6 sm:px-14 sm:py-16"
    >
      <div class="flex w-full max-w-[440px] flex-col gap-[18px]">
        {{yield}}
      </div>
    </main>
  </div>
</template>;

export default AuthLayout;
