import React, { useState, useMemo } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown, ChevronLeft, ChevronRight, Inbox } from 'lucide-react';
import { Button } from './Button';

export function Table({
  columns = [],
  data = [],
  keyExtractor,
  isLoading = false,
  emptyText = 'No records found',
  pageSize = 10,
  onRowClick,
  stickyHeader = true,
}) {
  const [sortKey, setSortKey] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);

  const handleSort = (key) => {
    if (sortKey === key) {
      if (sortDirection === 'asc') setSortDirection('desc');
      else {
        setSortKey(null);
        setSortDirection('asc');
      }
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const sortedData = useMemo(() => {
    if (!sortKey || !Array.isArray(data)) return data || [];
    return [...data].sort((a, b) => {
      const valA = a?.[sortKey];
      const valB = b?.[sortKey];
      if (valA === valB) return 0;
      if (valA === undefined || valA === null) return 1;
      if (valB === undefined || valB === null) return -1;
      if (typeof valA === 'number' && typeof valB === 'number') {
        return sortDirection === 'asc' ? valA - valB : valB - valA;
      }
      return sortDirection === 'asc'
        ? String(valA).localeCompare(String(valB))
        : String(valB).localeCompare(String(valA));
    });
  }, [data, sortKey, sortDirection]);

  const totalPages = Math.ceil(sortedData.length / pageSize) || 1;
  const paginatedData = sortedData.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  return (
    <div className="flex flex-col w-full rounded-xl border border-[#162235] bg-[#0d1524] overflow-hidden shadow-xl min-w-0">
      <div className="overflow-x-auto min-w-0">
        <table className="w-full text-left border-collapse text-xs min-w-[500px]">
          <thead>
            <tr
              className={`border-b border-[#162235] bg-[#090e17] text-slate-400 font-mono uppercase text-[11px] tracking-wider ${
                stickyHeader ? 'sticky top-0 z-10' : ''
              }`}
            >
              {columns.map((col) => (
                <th
                  key={col.key}
                  style={{ width: col.width }}
                  onClick={() => col.sortable && handleSort(col.key)}
                  className={`px-4 py-3 font-semibold select-none ${
                    col.sortable ? 'cursor-pointer hover:text-slate-200 transition-colors' : ''
                  } ${
                    col.align === 'right'
                      ? 'text-right'
                      : col.align === 'center'
                      ? 'text-center'
                      : 'text-left'
                  }`}
                >
                  <div
                    className={`inline-flex items-center gap-1.5 ${
                      col.align === 'right'
                        ? 'justify-end'
                        : col.align === 'center'
                        ? 'justify-center'
                        : 'justify-start'
                    }`}
                  >
                    <span>{col.header}</span>
                    {col.sortable && (
                      <span className="text-slate-500">
                        {sortKey === col.key ? (
                          sortDirection === 'asc' ? (
                            <ArrowUp className="h-3 w-3 text-cyan-400" />
                          ) : (
                            <ArrowDown className="h-3 w-3 text-cyan-400" />
                          )
                        ) : (
                          <ArrowUpDown className="h-3 w-3 opacity-40 hover:opacity-100" />
                        )}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#162235]/60 text-slate-200 font-mono">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="animate-pulse">
                  {columns.map((col, j) => (
                    <td key={j} className="px-4 py-3.5">
                      <div className="h-3.5 bg-slate-800/80 rounded w-3/4" />
                    </td>
                  ))}
                </tr>
              ))
            ) : paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-12 text-center text-slate-500">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <Inbox className="h-8 w-8 text-slate-600" />
                    <p className="text-sm font-medium">{emptyText}</p>
                  </div>
                </td>
              </tr>
            ) : (
              paginatedData.map((item, idx) => {
                const rowKey = keyExtractor ? keyExtractor(item, idx) : item.id || item.symbol || idx;
                return (
                  <tr
                    key={rowKey}
                    onClick={() => onRowClick?.(item)}
                    className={`transition-colors hover:bg-slate-800/40 ${
                      onRowClick ? 'cursor-pointer' : ''
                    }`}
                  >
                    {columns.map((col) => (
                      <td
                        key={col.key}
                        className={`px-4 py-3 font-medium ${
                          col.align === 'right'
                            ? 'text-right num-tabular'
                            : col.align === 'center'
                            ? 'text-center'
                            : 'text-left'
                        }`}
                      >
                        {col.accessor ? col.accessor(item) : item[col.key] ?? '—'}
                      </td>
                    ))}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-2.5 border-t border-[#162235] bg-[#090e17] text-xs text-slate-400 font-mono">
          <div>
            Showing <span className="text-slate-200">{(currentPage - 1) * pageSize + 1}</span> to{' '}
            <span className="text-slate-200">
              {Math.min(currentPage * pageSize, sortedData.length)}
            </span>{' '}
            of <span className="text-slate-200">{sortedData.length}</span> entries
          </div>
          <div className="flex items-center gap-1.5">
            <Button
              variant="outline"
              size="xs"
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            >
              <ChevronLeft className="h-3.5 w-3.5" />
            </Button>
            <span>
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="xs"
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            >
              <ChevronRight className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
