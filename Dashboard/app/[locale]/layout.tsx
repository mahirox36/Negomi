import {NextIntlClientProvider, hasLocale} from 'next-intl';
import {notFound} from 'next/navigation';
import {routing} from '@/i18n/routing';

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{locale: string}>;
}) {
  // Ensure that the incoming `locale` is valid
  const {locale} = await params;

  // Debugging logs to verify locale and hasLocale behavior
  console.log('Locale received:', locale);
  console.log('Available locales:', routing.locales);

  if (!hasLocale(routing.locales, locale)) {
    console.error('Invalid locale:', locale);
    notFound();
  }

  // Debugging log to verify messages loading
  const messages = (await import(`../../messages/${locale}.json`)).default;

  return (
    <NextIntlClientProvider locale={locale} messages={messages}>
      {children}
    </NextIntlClientProvider>
  );
}