export default function TestPage() {
  return (
    <div style={{ padding: '40px', backgroundColor: '#f0f0f0', minHeight: '100vh' }}>
      <h1 style={{ color: '#333', fontSize: '32px', marginBottom: '20px' }}>
        ✅ Next.js is Working!
      </h1>
      <p style={{ color: '#666', fontSize: '18px', marginBottom: '10px' }}>
        If you can see this page, Next.js is rendering correctly.
      </p>
      <p style={{ color: '#666', fontSize: '18px', marginBottom: '10px' }}>
        The issue is likely in the AuthContext or main pages.
      </p>
      <div style={{ marginTop: '30px', padding: '20px', backgroundColor: 'white', borderRadius: '8px' }}>
        <h2 style={{ color: '#333', fontSize: '24px', marginBottom: '15px' }}>
          Diagnostic Info:
        </h2>
        <ul style={{ color: '#666', fontSize: '16px', lineHeight: '1.8' }}>
          <li>✅ Next.js Server: Running</li>
          <li>✅ React Rendering: Working</li>
          <li>✅ Routing: Functional</li>
        </ul>
      </div>
      <div style={{ marginTop: '20px' }}>
        <a href="/" style={{ color: '#0070f3', textDecoration: 'underline' }}>
          Go back to homepage
        </a>
      </div>
    </div>
  );
}
