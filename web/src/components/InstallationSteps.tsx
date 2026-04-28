const steps = [
  "python -m venv .venv",
  ".\\.venv\\Scripts\\Activate.ps1",
  "python -m pip install --upgrade pip",
  "pip install -r requirements.txt",
  "python -m handos",
];

export function InstallationSteps() {
  return (
    <ol className="install-steps">
      {steps.map((step) => (
        <li key={step}>
          <code>{step}</code>
        </li>
      ))}
    </ol>
  );
}
