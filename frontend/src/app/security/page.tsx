import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Security | Spotyfinder",
  description: "Security policy and vulnerability reporting for Spotyfinder.",
};

export default function SecurityPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col gap-12 py-24 px-8 bg-white dark:bg-black sm:px-16">
        <div>
          <Link
            href="/"
            className="text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
          >
            ← Back to Home
          </Link>
        </div>

        <div>
          <h1 className="text-4xl font-bold tracking-tight text-black dark:text-white">
            Security Policy
          </h1>
          <p className="mt-4 text-lg text-zinc-600 dark:text-zinc-400">
            The security of Spotyfinder is important to us. We appreciate the
            efforts of security researchers and users who responsibly disclose
            vulnerabilities.
          </p>
        </div>

        <section>
          <h2 className="text-2xl font-semibold text-black dark:text-white mb-4">
            Supported Versions
          </h2>
          <p className="text-zinc-600 dark:text-zinc-400 mb-4">
            Only the latest version on the{" "}
            <code className="rounded bg-zinc-100 dark:bg-zinc-800 px-1.5 py-0.5 text-sm font-mono">
              main
            </code>{" "}
            branch receives security updates. We recommend always running the
            most recent version.
          </p>
          <div className="overflow-hidden rounded-lg border border-zinc-200 dark:border-zinc-800">
            <table className="w-full text-sm">
              <thead className="bg-zinc-100 dark:bg-zinc-800 text-left">
                <tr>
                  <th className="px-4 py-3 font-semibold text-zinc-700 dark:text-zinc-300">
                    Version
                  </th>
                  <th className="px-4 py-3 font-semibold text-zinc-700 dark:text-zinc-300">
                    Supported
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
                <tr>
                  <td className="px-4 py-3 text-zinc-700 dark:text-zinc-300">
                    latest (main branch)
                  </td>
                  <td className="px-4 py-3 text-green-600 dark:text-green-400 font-medium">
                    ✅ Yes
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-zinc-700 dark:text-zinc-300">
                    older branches
                  </td>
                  <td className="px-4 py-3 text-red-600 dark:text-red-400 font-medium">
                    ❌ No
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-black dark:text-white mb-4">
            Reporting a Vulnerability
          </h2>
          <p className="text-zinc-600 dark:text-zinc-400 mb-4">
            Please <strong className="text-zinc-900 dark:text-zinc-100">do not</strong> open a
            public GitHub issue for security vulnerabilities. Instead, report
            them responsibly:
          </p>
          <ol className="list-decimal list-inside space-y-3 text-zinc-600 dark:text-zinc-400">
            <li>
              Open a{" "}
              <a
                href="https://github.com/rabbitglauser/Spotyfinder/security/advisories/new"
                target="_blank"
                rel="noopener noreferrer"
                className="underline underline-offset-2 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
              >
                GitHub Security Advisory
              </a>{" "}
              to report the vulnerability privately.
            </li>
            <li>
              Describe the vulnerability clearly, including steps to reproduce
              and potential impact.
            </li>
            <li>
              Optionally suggest a fix — we welcome any guidance you can
              provide.
            </li>
          </ol>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-black dark:text-white mb-4">
            Response Timeline
          </h2>
          <ul className="space-y-3 text-zinc-600 dark:text-zinc-400">
            <li>
              <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                Acknowledgement:
              </span>{" "}
              Within 3 business days of receiving your report.
            </li>
            <li>
              <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                Assessment:
              </span>{" "}
              Within 7 business days we will evaluate severity and impact.
            </li>
            <li>
              <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                Resolution:
              </span>{" "}
              We aim to release a fix within 30 days for critical
              vulnerabilities.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-black dark:text-white mb-4">
            Data &amp; Privacy
          </h2>
          <p className="text-zinc-600 dark:text-zinc-400">
            Spotyfinder uses the Spotify API to provide personalized music
            recommendations. We do not store your Spotify credentials. Any data
            processed is used solely to generate recommendations and is not
            shared with third parties.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-black dark:text-white mb-4">
            Security Best Practices for Contributors
          </h2>
          <ul className="list-disc list-inside space-y-2 text-zinc-600 dark:text-zinc-400">
            <li>Never commit secrets, API keys, or credentials to the repository.</li>
            <li>Sanitize all user inputs on both the frontend and backend.</li>
            <li>Keep dependencies up to date and review security advisories.</li>
            <li>
              Use parameterized queries or ORM methods to prevent SQL injection.
            </li>
            <li>Follow the principle of least privilege when handling data.</li>
          </ul>
        </section>

        <footer className="border-t border-zinc-200 dark:border-zinc-800 pt-6 text-sm text-zinc-500">
          <p>
            For general questions, see the{" "}
            <a
              href="https://github.com/rabbitglauser/Spotyfinder"
              target="_blank"
              rel="noopener noreferrer"
              className="underline underline-offset-2 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
            >
              Spotyfinder repository
            </a>
            .
          </p>
        </footer>
      </main>
    </div>
  );
}
