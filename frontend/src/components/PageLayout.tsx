/** Page layout component. */

interface PageLayoutProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

/**
 * Page layout component with consistent structure.
 */
export function PageLayout({ title, description, children }: PageLayoutProps) {
  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          <h1 className="mb-3">{title}</h1>
          {description && <p className="text-muted mb-4">{description}</p>}
          {children}
        </div>
      </div>
    </div>
  );
}
