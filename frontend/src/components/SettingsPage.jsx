export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="mt-2 text-gray-400">
          Configure integrations, LLM providers, and privacy settings
        </p>
      </div>

      <div className="space-y-6">
        {/* Integrations Section */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Integrations</h2>
          <div className="space-y-4">
            <SettingItem title="Standard Notes" status="Not configured" />
            <SettingItem title="Paperless-ngx" status="Not configured" />
            <SettingItem title="Email" status="Not configured" />
            <SettingItem title="RSS Feeds" status="Not configured" />
          </div>
        </div>

        {/* LLM Providers Section */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">LLM Providers</h2>
          <div className="space-y-4">
            <SettingItem title="Anthropic Claude" status="Not configured" />
            <SettingItem title="OpenAI" status="Not configured" />
            <SettingItem title="Ollama (Local)" status="Available" />
            <SettingItem title="Google Gemini" status="Not configured" />
          </div>
        </div>

        {/* Privacy Settings */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Privacy Settings</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Use local LLM for sensitive content</p>
                <p className="text-sm text-gray-400">
                  Content tagged as sensitive will only use local Ollama models
                </p>
              </div>
              <input type="checkbox" className="h-5 w-5" defaultChecked />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function SettingItem({ title, status }) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-gray-700">
      <span className="font-medium">{title}</span>
      <span className="text-sm text-gray-400">{status}</span>
    </div>
  )
}
